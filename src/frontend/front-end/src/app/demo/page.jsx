import React from 'react';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import Link from 'next/link';
import { csvParse } from 'd3';
import VehicleExplorer from './VehicleExplorer';
import styles from './demo.module.css';

export default async function DemoPage() {
  const csv = await readFile(path.join(process.cwd(), 'public', 'vehicles.csv'), 'utf8');
  const rows = csvParse(csv, (row) => ({
    year: Number(row['model year']),
    vehicleClass: row['vehicle class'],
    engine: Number(row['Engine size (L)']),
    consumption: Number(row['Fuel consumption inside cities (l/100km)']),
  }));
  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.brand}>JourneyAI</div>
        <span className={styles.sectionName}>Sample dashboard</span>
        <Link href="/login" prefetch={false} className={styles.signIn}>Sign in</Link>
      </header>
      <main className={styles.main}>
        <h1>How did city fuel use change?</h1>
        <p className={styles.intro}>
          Explore six model years of synthetic vehicle data. Choose a vehicle class
          to see how a finding can lead to a reporting question.
        </p>
        <VehicleExplorer rows={Array.from(rows)} />
        <footer className={styles.footer}>
          <a href="/vehicles.csv" download>Download the sample CSV</a>
          <Link href="/register" prefetch={false}>Explore your own dataset →</Link>
        </footer>
      </main>
    </div>
  );
}
