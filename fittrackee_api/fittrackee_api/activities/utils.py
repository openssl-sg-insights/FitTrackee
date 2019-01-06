import hashlib
import os
import tempfile
import zipfile
from datetime import datetime, timedelta

import gpxpy.gpx
import pytz
from fittrackee_api import appLog, db
from flask import current_app
from sqlalchemy import exc
from staticmap import Line, StaticMap
from werkzeug.utils import secure_filename

from ..users.models import User
from .models import Activity, ActivitySegment, Sport
from .utils_files import get_absolute_file_path
from .utils_weather import get_weather


class ActivityException(Exception):
    def __init__(self, status, message, e):
        self.status = status
        self.message = message
        self.e = e


def get_datetime_with_tz(timezone, activity_date, gpx_data=None):
    activity_date_tz = None
    if timezone:
        user_tz = pytz.timezone(timezone)
        utc_tz = pytz.utc
        if gpx_data:
            # activity date in gpx is in UTC, but in naive datetime
            fmt = '%Y-%m-%d %H:%M:%S'
            activity_date_string = activity_date.strftime(fmt)
            activity_date_tmp = utc_tz.localize(
                datetime.strptime(activity_date_string, fmt))
            activity_date_tz = activity_date_tmp.astimezone(user_tz)
        else:
            activity_date_tz = user_tz.localize(activity_date)
            activity_date = activity_date_tz.astimezone(utc_tz)
            # make datetime 'naive' like in gpx file
            activity_date = activity_date.replace(tzinfo=None)

    return activity_date_tz, activity_date


def update_activity_data(activity, gpx_data):
    """activity could be a complete activity or an activity segment"""
    activity.pauses = gpx_data['stop_time']
    activity.moving = gpx_data['moving_time']
    activity.min_alt = gpx_data['elevation_min']
    activity.max_alt = gpx_data['elevation_max']
    activity.descent = gpx_data['downhill']
    activity.ascent = gpx_data['uphill']
    activity.max_speed = gpx_data['max_speed']
    activity.ave_speed = gpx_data['average_speed']
    return activity


def create_activity(
        user, activity_data, gpx_data=None
):
    activity_date = gpx_data['start'] if gpx_data else datetime.strptime(
        activity_data.get('activity_date'), '%Y-%m-%d %H:%M')
    activity_date_tz, activity_date = get_datetime_with_tz(
        user.timezone, activity_date, gpx_data)

    duration = gpx_data['duration'] if gpx_data \
        else timedelta(seconds=activity_data.get('duration'))
    distance = gpx_data['distance'] if gpx_data \
        else activity_data.get('distance')
    title = gpx_data['name'] if gpx_data \
        else activity_data.get('title')

    new_activity = Activity(
        user_id=user.id,
        sport_id=activity_data.get('sport_id'),
        activity_date=activity_date,
        distance=distance,
        duration=duration
    )
    new_activity.notes = activity_data.get('notes')

    if title is not None and title != '':
        new_activity.title = title
    else:
        sport = Sport.query.filter_by(id=new_activity.sport_id).first()
        fmt = "%Y-%m-%d %H:%M:%S"
        activity_datetime = (
            activity_date_tz.strftime(fmt)
            if activity_date_tz
            else new_activity.activity_date.strftime(fmt))
        new_activity.title = f'{sport.label} - {activity_datetime}'

    if gpx_data:
        new_activity.gpx = gpx_data['filename']
        new_activity.bounds = gpx_data['bounds']
        update_activity_data(new_activity, gpx_data)
    else:
        new_activity.moving = duration
        new_activity.ave_speed = (None
                                  if duration.seconds == 0
                                  else float(new_activity.distance) /
                                  (duration.seconds / 3600))
        new_activity.max_speed = new_activity.ave_speed
    return new_activity


def create_segment(activity_id, segment_data):
    new_segment = ActivitySegment(
        activity_id=activity_id,
        segment_id=segment_data['idx']
    )
    new_segment.duration = segment_data['duration']
    new_segment.distance = segment_data['distance']
    update_activity_data(new_segment, segment_data)
    return new_segment


def update_activity(activity):
    """
    Note: only gpx_data is be updated for now (the gpx file is NOT modified)

    In a next version, map_data and weather_data will be updated
    (case of a modified gpx file, see issue #7)
    """
    gpx_data, _, _ = get_gpx_info(get_absolute_file_path(activity.gpx))
    updated_activity = update_activity_data(activity, gpx_data)
    updated_activity.duration = gpx_data['duration']
    updated_activity.distance = gpx_data['distance']
    db.session.flush()

    for segment_idx, segment in enumerate(updated_activity.segments):
        segment_data = gpx_data['segments'][segment_idx]
        updated_segment = update_activity_data(segment, segment_data)
        updated_segment.duration = segment_data['duration']
        updated_segment.distance = segment_data['distance']
        db.session.flush()

    return updated_activity


def edit_activity(activity, activity_data, auth_user_id):
    user = User.query.filter_by(id=auth_user_id).first()
    if activity_data.get('refresh'):
        activity = update_activity(activity)
    if activity_data.get('sport_id'):
        activity.sport_id = activity_data.get('sport_id')
    if activity_data.get('title'):
        activity.title = activity_data.get('title')
    if activity_data.get('notes'):
        activity.notes = activity_data.get('notes')
    if not activity.gpx:
        if activity_data.get('activity_date'):
            activity_date = datetime.strptime(
                activity_data.get('activity_date'), '%Y-%m-%d %H:%M')
            _, activity.activity_date = get_datetime_with_tz(
                user.timezone, activity_date)

        if activity_data.get('duration'):
            activity.duration = timedelta(
                seconds=activity_data.get('duration'))
            activity.moving = activity.duration

        if activity_data.get('distance'):
            activity.distance = activity_data.get('distance')

        activity.ave_speed = (None if activity.duration.seconds == 0
                              else float(activity.distance) /
                              (activity.duration.seconds / 3600))
        activity.max_speed = activity.ave_speed
    return activity


def get_gpx_data(parsed_gpx, max_speed, start, stopped_time_btwn_seg):
    gpx_data = {'max_speed': (max_speed / 1000) * 3600, 'start': start}

    duration = parsed_gpx.get_duration()
    gpx_data['duration'] = timedelta(seconds=duration) + stopped_time_btwn_seg

    ele = parsed_gpx.get_elevation_extremes()
    gpx_data['elevation_max'] = ele.maximum
    gpx_data['elevation_min'] = ele.minimum

    hill = parsed_gpx.get_uphill_downhill()
    gpx_data['uphill'] = hill.uphill
    gpx_data['downhill'] = hill.downhill

    mv = parsed_gpx.get_moving_data()
    gpx_data['moving_time'] = timedelta(seconds=mv.moving_time)
    gpx_data['stop_time'] = (timedelta(seconds=mv.stopped_time)
                             + stopped_time_btwn_seg)
    distance = mv.moving_distance + mv.stopped_distance
    gpx_data['distance'] = distance / 1000

    average_speed = distance / mv.moving_time if mv.moving_time > 0 else 0
    gpx_data['average_speed'] = (average_speed / 1000) * 3600

    return gpx_data


def open_gpx_file(gpx_file):
    gpx_file = open(gpx_file, 'r')
    gpx = gpxpy.parse(gpx_file)
    if len(gpx.tracks) == 0:
        return None
    return gpx


def get_gpx_info(gpx_file, update_map_data=True, update_weather_data=True):
    gpx = open_gpx_file(gpx_file)
    if gpx is None:
        return None

    gpx_data = {
        'name': gpx.tracks[0].name,
        'segments': []
    }
    max_speed = 0
    start = 0
    map_data = []
    weather_data = []
    segments_nb = len(gpx.tracks[0].segments)
    prev_seg_last_point = None
    no_stopped_time = timedelta(seconds=0)
    stopped_time_btwn_seg = no_stopped_time

    for segment_idx, segment in enumerate(gpx.tracks[0].segments):
        segment_start = 0
        segment_points_nb = len(segment.points)
        for point_idx, point in enumerate(segment.points):
            if point_idx == 0:
                # first gpx point => get weather
                if start == 0:
                    start = point.time
                    if update_weather_data:
                        weather_data.append(get_weather(point))

                # if a previous segment exists, calculate stopped time between
                # the two segments
                if prev_seg_last_point:
                    stopped_time_btwn_seg = point.time - prev_seg_last_point

            # last segment point
            if point_idx == (segment_points_nb - 1):
                prev_seg_last_point = point.time

                # last gpx point => get weather
                if segment_idx == (segments_nb - 1) and update_weather_data:
                    weather_data.append(get_weather(point))

            if update_map_data:
                map_data.append([
                    point.longitude, point.latitude
                ])
        segment_max_speed = (segment.get_moving_data().max_speed
                             if segment.get_moving_data().max_speed
                             else 0)

        if segment_max_speed > max_speed:
            max_speed = segment_max_speed

        segment_data = get_gpx_data(
            segment, segment_max_speed, segment_start, no_stopped_time
        )
        segment_data['idx'] = segment_idx
        gpx_data['segments'].append(segment_data)

    full_gpx_data = get_gpx_data(gpx, max_speed, start, stopped_time_btwn_seg)
    gpx_data = {**gpx_data, **full_gpx_data}

    if update_map_data:
        bounds = gpx.get_bounds()
        gpx_data['bounds'] = [
            bounds.min_latitude,
            bounds.min_longitude,
            bounds.max_latitude,
            bounds.max_longitude
        ]

    return gpx_data, map_data, weather_data


def get_chart_data(gpx_file):
    gpx = open_gpx_file(gpx_file)
    if gpx is None:
        return None

    chart_data = []
    first_point = None
    previous_point = None
    previous_distance = 0

    for segment_idx, segment in enumerate(gpx.tracks[0].segments):
        for point_idx, point in enumerate(segment.points):
            if segment_idx == 0 and point_idx == 0:
                first_point = point
            distance = (point.distance_3d(previous_point)
                        if (point.elevation
                            and previous_point
                            and previous_point.elevation)
                        else point.distance_2d(previous_point)
                        )
            distance = 0 if distance is None else distance
            distance += previous_distance
            speed = (round((segment.get_speed(point_idx) / 1000)*3600, 2)
                     if segment.get_speed(point_idx) is not None
                     else 0)
            chart_data.append({
                'distance': (round(distance / 1000, 2)
                             if distance is not None else 0),
                'duration': point.time_difference(first_point),
                'elevation': (round(point.elevation, 1)
                              if point.elevation is not None else 0),
                'speed': speed,
                'time': point.time,
            })
            previous_point = point
            previous_distance = distance

    return chart_data


def get_file_path(dir_path, filename):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_path = os.path.join(dir_path, filename)
    return file_path


def get_new_file_path(
        auth_user_id, activity_date, sport, old_filename=None, extension=None
):
    if not extension:
        extension = f".{old_filename.rsplit('.', 1)[1].lower()}"
    _, new_filename = tempfile.mkstemp(
        prefix=f'{activity_date}_{sport}_',
        suffix=extension
    )
    dir_path = os.path.join('activities', str(auth_user_id))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_path = os.path.join(dir_path,
                             new_filename.split('/')[-1])
    return file_path


def generate_map(map_filepath, map_data):
    m = StaticMap(400, 225, 10)
    line = Line(map_data, '#3388FF', 4)
    m.add_line(line)
    image = m.render()
    image.save(map_filepath)


def get_map_hash(map_filepath):
    """
    md5 hash is used as id instead of activity id, to retrieve map image
    (maps are sensitive data)
    """
    md5 = hashlib.md5()
    absolute_map_filepath = get_absolute_file_path(map_filepath)
    with open(absolute_map_filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
            md5.update(chunk)
    return md5.hexdigest()


def process_one_gpx_file(params, filename):
    try:
        gpx_data, map_data, weather_data = get_gpx_info(params['file_path'])
        auth_user_id = params['user'].id
        new_filepath = get_new_file_path(
            auth_user_id=auth_user_id,
            activity_date=gpx_data['start'],
            old_filename=filename,
            sport=params['sport_label']
        )
        absolute_gpx_filepath = get_absolute_file_path(new_filepath)
        os.rename(params['file_path'], absolute_gpx_filepath)
        gpx_data['filename'] = new_filepath

        map_filepath = get_new_file_path(
            auth_user_id=auth_user_id,
            activity_date=gpx_data['start'],
            extension='.png',
            sport=params['sport_label']
        )
        absolute_map_filepath = get_absolute_file_path(map_filepath)
        generate_map(absolute_map_filepath, map_data)
    except (gpxpy.gpx.GPXXMLSyntaxException, TypeError) as e:
        raise ActivityException('error', 'Error during gpx file parsing.', e)
    except Exception as e:
        raise ActivityException('error', 'Error during gpx processing.', e)

    try:
        new_activity = create_activity(
            params['user'], params['activity_data'], gpx_data)
        new_activity.map = map_filepath
        new_activity.map_id = get_map_hash(map_filepath)
        new_activity.weather_start = weather_data[0]
        new_activity.weather_end = weather_data[1]
        db.session.add(new_activity)
        db.session.flush()

        for segment_data in gpx_data['segments']:
            new_segment = create_segment(new_activity.id, segment_data)
            db.session.add(new_segment)
        db.session.commit()
        return new_activity
    except (exc.IntegrityError, ValueError) as e:
        raise ActivityException('fail', 'Error during activity save.', e)


def process_zip_archive(common_params, extract_dir):
    with zipfile.ZipFile(common_params['file_path'], "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    new_activities = []
    gpx_files_limit = os.getenv('REACT_APP_GPX_LIMIT_IMPORT')
    if gpx_files_limit and gpx_files_limit.isdigit():
        gpx_files_limit = int(gpx_files_limit)
    else:
        gpx_files_limit = 10
        appLog.error('GPX limit not configured, set to 10.')
    gpx_files_ok = 0

    for gpx_file in os.listdir(extract_dir):
        if ('.' in gpx_file and gpx_file.rsplit('.', 1)[1].lower()
                in current_app.config.get('ACTIVITY_ALLOWED_EXTENSIONS')):
            gpx_files_ok += 1
            if gpx_files_ok > gpx_files_limit:
                break
            file_path = os.path.join(extract_dir, gpx_file)
            params = common_params
            params['file_path'] = file_path
            new_activity = process_one_gpx_file(params, gpx_file)
            new_activities.append(new_activity)

    return new_activities


def process_files(auth_user_id, activity_data, activity_file, folders):
    filename = secure_filename(activity_file.filename)
    extension = f".{filename.rsplit('.', 1)[1].lower()}"
    file_path = get_file_path(folders['tmp_dir'], filename)
    sport = Sport.query.filter_by(id=activity_data.get('sport_id')).first()
    if not sport:
        raise ActivityException(
            'error',
            f"Sport id: {activity_data.get('sport_id')} does not exist",
            None
        )
    user = User.query.filter_by(id=auth_user_id).first()

    common_params = {
        'user': user,
        'activity_data': activity_data,
        'file_path': file_path,
        'sport_label': sport.label,
    }

    try:
        activity_file.save(file_path)
    except Exception as e:
        raise ActivityException('error', 'Error during activity file save.', e)

    if extension == ".gpx":
        return [process_one_gpx_file(common_params, filename)]
    else:
        return process_zip_archive(common_params, folders['extract_dir'])
