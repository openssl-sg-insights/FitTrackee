import { apiUrl } from '../utils'

export default class MpwoApi {

  static addActivity(formData) {
    const request = new Request(`${apiUrl}activities`, {
      method: 'POST',
      headers: new Headers({
        Authorization: `Bearer ${window.localStorage.getItem('authToken')}`,
      }),
      body: formData,
    })
    return fetch(request)
      .then(response => response.json())
      .catch(error => error)
  }

  static addActivityWithoutGpx(data) {
    const request = new Request(`${apiUrl}activities/no_gpx`, {
      method: 'POST',
      headers: new Headers({
        'Content-Type': 'application/json',
        Authorization: `Bearer ${window.localStorage.getItem('authToken')}`,
      }),
      body: JSON.stringify(data)
    })
    return fetch(request)
      .then(response => response.json())
      .catch(error => error)
  }

  static getActivityGpx(activityId) {
    const request = new Request(`${apiUrl}activities/${activityId}/gpx`, {
      method: 'GET',
      headers: new Headers({
        Authorization: `Bearer ${window.localStorage.getItem('authToken')}`,
      }),
    })
    return fetch(request)
      .then(response => response.json())
      .catch(error => error)
  }

}