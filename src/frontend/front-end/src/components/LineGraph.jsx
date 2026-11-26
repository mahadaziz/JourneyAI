/* eslint-disable max-len */

'use client';

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

function LineGraph({
  rows, xField, yField, title,
}) {
  const d3Container = useRef(null);

  useEffect(() => {
    if (rows && d3Container.current) {
      const data = rows.map((item) => ({
        xValue: item[xField],
        yValue: item[yField],
      }));

      const svg = d3.select(d3Container.current);
      svg.selectAll('*').remove();
      const margin = {
        top: 44, right: 34, bottom: 48, left: 70,
      };
      const width = 700 - margin.left - margin.right;
      const height = 400 - margin.top - margin.bottom;

      const plot = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

      const x = d3.scaleLinear()
        .domain(d3.extent(data, (d) => d.xValue))
        .range([0, width]);
      plot.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x).ticks(Math.min(data.length - 1, 8)).tickFormat(d3.format('d')));

      const yPadding = (d3.max(data, (d) => d.yValue) - d3.min(data, (d) => d.yValue)) * 0.1 || 1;

      const y = d3.scaleLinear()
        .domain([d3.min(data, (d) => d.yValue) - yPadding, d3.max(data, (d) => d.yValue) + yPadding])
        .range([height, 0]);
      plot.append('g')
        .call(d3.axisLeft(y));

      const line = d3.line()
        .x((d) => x(d.xValue))
        .y((d) => y(d.yValue));

      const bisect = d3.bisector((d) => d.xValue).center;

      const focus = plot
        .append('g')
        .append('circle')
        .style('fill', 'none')
        .attr('stroke', 'black')
        .attr('r', 8.5)
        .style('opacity', 0);

      const focusText = plot
        .append('g')
        .append('text')
        .style('opacity', 0)
        .attr('text-anchor', 'start')
        .attr('alignment-baseline', 'middle');

      plot.append('path')
        .datum(data)
        .attr('fill', 'none')
        .attr('stroke', 'steelblue')
        .attr('stroke-width', 1.5)
        .attr('d', line);

      const mouseover = () => {
        focus.style('opacity', 1);
        focusText.style('opacity', 1);
      };

      const mousemove = (event) => {
        const [xPos] = d3.pointer(event);
        const x0 = x.invert(xPos);
        const i = bisect(data, x0);
        if (data[i]) {
          const tooltipWidth = focusText.node().getBBox().width;
          const offset = 15;
          let xPosition = x(data[i].xValue) + offset;
          if (xPosition + tooltipWidth > width) {
            xPosition -= tooltipWidth * 1.2;
          }
          focus
            .attr('cx', x(data[i].xValue))
            .attr('cy', y(data[i].yValue));
          focusText
            .text(`${data[i].xValue}: ${data[i].yValue.toFixed(2)}`)
            .attr('x', xPosition)
            .attr('y', y(data[i].yValue));
        }
      };

      const mouseout = () => {
        focus.style('opacity', 0);
        focusText.style('opacity', 0);
      };

      plot.append('rect')
        .style('fill', 'none')
        .style('pointer-events', 'all')
        .attr('width', width)
        .attr('height', height)
        .on('mouseover', mouseover)
        .on('mousemove', mousemove)
        .on('mouseout', mouseout);

      plot.append('text')
        .attr('text-anchor', 'middle')
        .attr('x', width / 2)
        .attr('y', height + 38)
        .text(xField);

      plot.append('text')
        .attr('text-anchor', 'middle')
        .attr('transform', 'rotate(-90)')
        .attr('y', -margin.left + 15)
        .attr('x', -height / 2)
        .text(yField);

      plot.append('text')
        .attr('x', width / 2)
        .attr('y', -20)
        .attr('text-anchor', 'middle')
        .attr('font-size', '16px')
        .style('font-weight', '600')
        .text(title);
    }
  }, [rows, xField, yField, title]);

  return (
    <svg ref={d3Container} role="img" aria-label={title} viewBox="0 0 700 400" width="700" style={{ maxWidth: 'var(--line-chart-max-width, 75vw)', height: 'auto' }} />
  );
}

export default LineGraph;
