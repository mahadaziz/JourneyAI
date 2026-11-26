'use client';

import React, { useState } from 'react';
import { mean, rollups } from 'd3';
import LineGraph from '../../components/LineGraph';
import styles from './demo.module.css';

const yearLabel = 'Model year';
const fuelLabel = 'City fuel use (L/100 km)';

export default function VehicleExplorer({ rows }) {
  const [vehicleClass, setVehicleClass] = useState('');
  const classes = [...new Set(rows.map((row) => row.vehicleClass))];
  const selected = vehicleClass ? rows.filter((row) => row.vehicleClass === vehicleClass) : rows;
  const points = rollups(selected, (group) => ({
    [fuelLabel]: mean(group, (row) => row.consumption),
    engine: mean(group, (row) => row.engine),
  }), (row) => row.year)
    .map(([year, values]) => ({ [yearLabel]: year, ...values }))
    .sort((a, b) => a[yearLabel] - b[yearLabel]);
  const first = points[0];
  const last = points[points.length - 1];
  const groupName = vehicleClass ? `${vehicleClass} vehicles` : 'All vehicles';

  return (
    <div className={styles.grid}>
      <section className={styles.chartPanel} aria-labelledby="chart-heading">
        <div className={styles.chartHeader}>
          <div>
            <h2 id="chart-heading">City driving</h2>
            <p>{`${selected.length} sample records`}</p>
          </div>
          <label className={styles.filter} htmlFor="vehicle-class">
            Vehicle class
            <select
              id="vehicle-class"
              value={vehicleClass}
              onChange={(event) => setVehicleClass(event.target.value)}
            >
              <option value="">All vehicles</option>
              {classes.map((name) => <option key={name}>{name}</option>)}
            </select>
          </label>
        </div>
        <LineGraph
          rows={points}
          xField={yearLabel}
          yField={fuelLabel}
          title={`Average city fuel use · ${groupName}`}
        />
        <details className={styles.tableDetails}>
          <summary>View chart data</summary>
          <table>
            <caption className="sr-only">{`Average city fuel use for ${groupName}`}</caption>
            <thead>
              <tr>
                <th scope="col">Model year</th>
                <th scope="col">L/100 km</th>
              </tr>
            </thead>
            <tbody>
              {points.map((point) => (
                <tr key={point[yearLabel]}>
                  <th scope="row">{point[yearLabel]}</th>
                  <td>{point[fuelLabel].toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </details>
      </section>
      <section className={styles.notes} aria-labelledby="notes-heading">
        <h2 id="notes-heading">Reporting notes</h2>
        <h3>Finding</h3>
        <p aria-live="polite">
          {`${groupName} averaged `}
          <strong>{`${first[fuelLabel].toFixed(1)} L/100 km`}</strong>
          {` in ${first[yearLabel]} and `}
          <strong>{`${last[fuelLabel].toFixed(1)} L/100 km`}</strong>
          {` in ${last[yearLabel]}. Average engine size also fell, `}
          {`from ${first.engine.toFixed(1)} to ${last.engine.toFixed(1)} litres.`}
        </p>
        <h3>Example hypothesis</h3>
        <p>
          Smaller engines may explain some of the decline. A reporter could test this
          with more vehicles, comparing similar models within each class and year.
        </p>
      </section>
    </div>
  );
}
