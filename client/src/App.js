import React, { useState, useEffect } from "react"

const Standings = () => {
  const [standings, setStandings] = useState([]);

  useEffect(() => {
    const fetchStandings = async () => {
      try {
        const response = await fetch('/api/standings');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setStandings(data.standings);
      } catch (error) {
        console.error('Error fetching standings:', error);
      }
    };

    fetchStandings();
  }, []);

  return (
    <div>
      <h2>Current LaLiga Standings</h2>
      <table>
        <thead>
          <tr>
            <th>Team</th>
            <th>GP</th>
            <th>W</th>
            <th>D</th>
            <th>L</th>
            <th>F</th>
            <th>A</th>
            <th>GD</th>
            <th>P</th>
          </tr>
        </thead>
        <tbody>
          {standings.map((team, index) => (
            <tr key={index}>
              <td>{team.Team}</td>
              <td>{team.GP}</td>
              <td>{team.W}</td>
              <td>{team.D}</td>
              <td>{team.L}</td>
              <td>{team.F}</td>
              <td>{team.A}</td>
              <td>{team.GD}</td>
              <td>{team.P}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

const Schedule = () => {
  const [schedule, setSchedule] = useState([]);

  useEffect(() => {
    const fetchSchedule = async () => {
      try {
        const response = await fetch('/api/schedule');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        console.log('Fetched schedule:', data);
        setSchedule(data.schedule);
      } catch (error) {
        console.error('Error fetching schedule:', error);
      }
    };

    fetchSchedule();
  }, []);

  return (
    <div>
      <h2>Upcoming LaLiga Matches</h2>
      <table>
        <thead>
          <tr>
            <th>Team 1</th>
            <th>Team 2</th>
            <th>Location</th>
            <th>Online Betting Odds</th>
          </tr>
        </thead>
        <tbody>
          {schedule.map((match, index) => (
            <tr key={index}>
              <td>{match['Team 1']}</td>
              <td>{match['Team 2']}</td>
              <td>{match['Location']}</td>
              <td>{match['ODDS BY']}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

function App() {
  return (
    <div>
      <div id="header">
        <img src="LaLiga.jpg" height="110px" width ="340px" />
        <h1>Match Predictor</h1>
      </div>
      <Standings />
      <Schedule />
    </div>
  )
}

export default App;