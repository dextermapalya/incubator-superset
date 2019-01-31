/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
import React from 'react';
import { Modal } from 'react-bootstrap';
import PropTypes from 'prop-types';
import { t } from '@superset-ui/translation';
import { SupersetClient } from '@superset-ui/connection';
import Omnibar from 'omnibar';
import {
  Logger,
  ActionLog,
  LOG_ACTIONS_OMNIBAR_TRIGGERED,
} from '../logger';

const propTypes = {
  impressionId: PropTypes.string.isRequired,
  dashboardId: PropTypes.number.isRequired,
};

const getDashboards = query =>
  // todo: Build a dedicated endpoint for dashboard searching
  // i.e. superset/v1/api/dashboards?q=${query}
   SupersetClient.get({
        endpoint: `/dashboardasync/api/read?_oc_DashboardModelViewAsync=changed_on&_od_DashboardModelViewAsync=desc&_flt_2_dashboard_title=${query}`,
      })
        .then(({ json }) => json.result.map(item => ({
            title: item.dashboard_title,
            ...item,
          }),
        ))
        .catch(() => ({
            title: t('An error occurred while fethching Dashboards'),
        }));

class OmniContainer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      showOmni: false,
    };
    this.handleKeydown = this.handleKeydown.bind(this);
  }

  componentDidMount() {
    document.addEventListener('keydown', this.handleKeydown);
  }

  componentWillUnmount() {
    document.removeEventListener('keydown', this.handleKeydown);
  }

  handleKeydown(event) {
    const controlOrCommand = event.ctrlKey || event.metaKey;
    if (controlOrCommand) {
      const isK = event.key === 'k' || event.keyCode === 83;
      if (isK) {
        this.setState({ showOmni: !this.state.showOmni });

        // Get first input in the modal div
        document
          .getElementsByClassName('modal-dialog')[0]
          .getElementsByTagName('input')[0]
          .focus();

        Logger.send(
          new ActionLog({
            impressionId: this.props.impressionId, // impo
            source: 'dashboard',
            sourceId: this.props.dashboardId, // sourceId: this.props.dashboardId
            eventNames: LOG_ACTIONS_OMNIBAR_TRIGGERED,
          }),
        );
      }
    }
  }

  render() {
      return (
        <Modal show={this.state.showOmni} ref={this.exampleRef}>
          <Omnibar placeholder="Search for dashboards.." extensions={[getDashboards]} />
        </Modal>
      );
  }
}

OmniContainer.propTypes = propTypes;
export default OmniContainer;