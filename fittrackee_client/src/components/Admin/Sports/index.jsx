import React from 'react'
import { connect } from 'react-redux'
import { Helmet } from 'react-helmet'

import Message from '../../Common/Message'
import { getOrUpdateData } from '../../../actions'
import { history } from '../../../index'

class AdminSports extends React.Component {
  componentDidMount() {
    this.props.loadSports()
  }

  render() {
    const { message, sports, t, updateSport } = this.props
    return (
      <div>
        <Helmet>
          <title>FitTrackee - {t('administration:Administration')}</title>
        </Helmet>
        {message && <Message message={message} t={t} />}
        <div className="container">
          <div className="row">
            <div className="col card">
              <div className="card-body">
                {sports.length > 0 && (
                  <table className="table">
                    <thead>
                      <tr>
                        <th>{t('administration:id')}</th>
                        <th>{t('administration:Image')}</th>
                        <th>{t('administration:Label')}</th>
                        <th>{t('administration:Active')}</th>
                        <th>{t('administration:Actions')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sports.map(sport => (
                        <tr key={sport.id}>
                          <th scope="row">{sport.id}</th>
                          <td>
                            <img
                              className="admin-img"
                              src={sport.img ? sport.img : '/img/photo.png'}
                              alt="sport logo"
                            />
                          </td>
                          <td>{t(`sports:${sport.label}`)}</td>
                          <td>
                            {sport.is_active ? (
                              <i
                                className="fa fa-check-square-o custom-fa"
                                aria-hidden="true"
                                data-toggle="tooltip"
                              />
                            ) : (
                              <i
                                className="fa fa-square-o custom-fa"
                                aria-hidden="true"
                                data-toggle="tooltip"
                              />
                            )}
                          </td>
                          <td>
                            {sport._can_be_disabled ? (
                              <input
                                type="submit"
                                className={`btn btn-${
                                  sport.is_active ? 'dark' : 'primary'
                                } btn-sm`}
                                value={
                                  sport.is_active
                                    ? t('administration:Disable')
                                    : t('administration:Enable')
                                }
                                onClick={() =>
                                  updateSport(sport.id, !sport.is_active)
                                }
                              />
                            ) : (
                              <span className="admin-message">
                                {t('administration:activities exist')}
                              </span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
                <input
                  type="submit"
                  className="btn btn-secondary btn-lg btn-block"
                  onClick={() => history.push('/admin/')}
                  value={t('administration:Back')}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

export default connect(
  state => ({
    message: state.message,
    sports: state.sports.data,
    user: state.user,
  }),
  dispatch => ({
    loadSports: () => {
      dispatch(getOrUpdateData('getData', 'sports'))
    },
    updateSport: (sportId, isActive) => {
      const data = { id: sportId, is_active: isActive }
      dispatch(getOrUpdateData('updateData', 'sports', data, false))
    },
  })
)(AdminSports)