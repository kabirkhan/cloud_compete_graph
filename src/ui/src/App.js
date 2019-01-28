import React, { Component } from 'react';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import blueGrey from '@material-ui/core/colors/blueGrey';
import green from '@material-ui/core/colors/green';
import blue from '@material-ui/core/colors/blue';
import AppBar from '@material-ui/core/AppBar';
import Button from '@material-ui/core/Button';
import './App.css';
import Navbar from './Navbar';
import Graph from './Graph';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';

const theme = createMuiTheme({
  palette: {
    primary: blueGrey,
  },
});

class App extends Component {
  constructor(props) {
    super(props);

    this.state = {
      graph: {
        isLoading: true,
        nodes: [],
        links: []
      }
    }
  }
  componentDidMount(props) {
    const { graph } = this.state;
    this.setState({
      graph: {...graph, isLoading: true}
    }, () => {
      setTimeout(() => {
        this.setState({
          graph: {
            isLoading: false,  
            nodes: [{ id: 'Harry' }, { id: 'Sally' }, { id: 'Alice' }],
            links: [{ source: 'Harry', target: 'Sally' }, { source: 'Harry', target: 'Alice' }]          
          }
        })
      }, 1000)
    })
  }

  render() {
    return (
      <MuiThemeProvider theme={theme}>
        <Navbar/>
        <Grid container spacing={24}>
          <Grid item xs={8}>
            <Graph data={this.state.graph}/>
          </Grid>
          <Grid item xs={4}>
            Hey
          </Grid>          
        </Grid>
      </MuiThemeProvider>
    );
  }
}

export default App;
