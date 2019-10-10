import React from 'react';
import ReactDOM from 'react-dom';

import { Avatar, ClusterSchematic } from './clusterschematic.jsx'
import { SimulationList } from './simulationlist.jsx'
import { colourJob } from './receivesimulations.jsx'

import css from '../assets/styles/activity.sass'

class Layout extends React.Component {
  constructor(props) {
    super(props);

    const cores = 16;

    this.state = {
      nodeInfo: Array(cores)
        .fill(0)
        .map((v) => {
          return {
            job: {},
            cpu: 0,
            cpuHistory: [],
            cpuColourHistory: []
          };
        }),
      cpuHistoryMax: 50,
      dataUrl: props.dataUrl,
      serverUpdateInterval: 50,
      pending: [],
      running: [],
    };

  }

  componentDidMount() {
    this.fetchActivity();
    setInterval(this.fetchActivity.bind(this), this.state
      .serverUpdateInterval);
  }

  // fetch best simulations from server and update in component state
  fetchActivity() {
    fetch(this.state.dataUrl)
      .then(res => res.json())
      .then(
        (result) => {
          var newNodeInfo = this.state.nodeInfo.map((info, index) => {
            // add previous value of CPU to cpuHistory
            info.cpuHistory.push(info.cpu)
            info.cpuColourHistory.push(info.job.colour)

            // limit length to this.state.cpuHistoryMax
            const start = info.cpuHistory.length - this.state
              .cpuHistoryMax;
            const end = info.cpuHistory.length;
            if (start >= 0) {
              info.cpuHistory = info.cpuHistory.slice(start, end);
              info.cpuColourHistory = info.cpuColourHistory.slice(start,
                end);
            }

            // update current CPU value
            info.cpu = result.cpu_usage[index]

            return info;
          });

          // duplicate job info on each core
          // data is duplicated to simplify logic, but
          result.running.forEach((job) => {
            job['cores'].forEach((core) => {
              newNodeInfo[core]['job'] = job;
            });
          });

          // colour the jobs using the colourJob function
          // once again, duplication simplifies logic
          // (i.e. when dealing with empty jobs in newNodeInfo)
          const running = result.running.map((job) => colourJob(job))
          const pending = result.pending.map((job) => colourJob(job))

          this.setState({
            nodeInfo: newNodeInfo,
            pending: pending,
            running: running,

          });
        },
        (error) => {
          console.log("failed to load data from " + this.state.dataUrl);
        }
      );
  }

  render() {
    return (
      <div id="layout">
          <div className="pane lhs">
              <ClusterSchematic info={this.state.nodeInfo} />
          </div>
          <SimulationList simulations={this.state.running} title="Running" percentageKey='progress'/>
          <SimulationList simulations={this.state.pending} title="Waiting" percentageKey='progress'/>
      </div>
    );
  }
}

ReactDOM.render(
  <Layout dataUrl={"/cluster/activity"} />,
  document.getElementById('root-activity')
);
