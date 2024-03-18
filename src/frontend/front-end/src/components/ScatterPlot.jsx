/* eslint-disable max-len */

'use client';

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

function ScatterPlot({ chartData, xField, yField }) {
  const d3Container = useRef(null);
  const tooltipRef = useRef(null);

  useEffect(() => {
    if (chartData && d3Container.current) {
      const data = chartData[5].map((item) => ({
        xValue: item[xField],
        yValue: item[yField],
      }));
      const svg = d3.select(d3Container.current);

      const margin = {
        top: 15, right: 0, bottom: 25, left: 50,
      };
      const width = 700 - margin.left - margin.right;
      const height = 400 - margin.top - margin.bottom;

      svg.attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

      const x = d3.scaleLinear()
        .domain([d3.min(data, (d) => d.xValue) - 2, d3.max(data, (d) => d.xValue) + 1])
        .range([margin.left, width + margin.left]);
      svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x).tickFormat(d3.format('d')));

      const yPadding = (d3.max(data, (d) => d.yValue) - d3.min(data, (d) => d.yValue)) * 0.1;
      const y = d3.scaleLinear()
        .domain([d3.min(data, (d) => d.yValue) - yPadding, d3.max(data, (d) => d.yValue) + yPadding])
        .range([height, 0]);
      svg.append('g')
        .attr('transform', `translate(${margin.left},0)`)
        .call(d3.axisLeft(y));

      const tooltip = d3.select(tooltipRef.current)
        .style('opacity', 0)
        .attr('class', 'tooltip')
        .style('position', 'absolute')
        .style('background-color', 'white')
        .style('border', 'solid')
        .style('border-width', '2px')
        .style('border-radius', '5px')
        .style('padding', '5px')
        .style('pointer-events', 'none');

      const mouseover = (event, d) => {
        tooltip.style('opacity', 1);
      };

      const mousemove = (event, d) => {
        tooltip
          .html(`${xField}: ${d.xValue.toFixed(3)}<br>${yField}: ${d.yValue.toFixed(3)}`)
          .style('left', `${event.pageX - 600}px`)
          .style('top', `${event.pageY - 100}px`);
      };

      const mouseleave = (event, d) => {
        tooltip.style('opacity', 0);
      };

      svg.selectAll('dot')
        .data(data)
        .enter()
        .append('circle')
        .attr('class', 'dot')
        .attr('cx', (d) => x(d.xValue))
        .attr('cy', (d) => y(d.yValue))
        .attr('r', 5)
        .attr('fill', '#69b3a2')
        .on('mouseover', mouseover)
        .on('mousemove', mousemove)
        .on('mouseleave', mouseleave);

      svg.append('text')
        .attr('text-anchor', 'end')
        .attr('x', width / 2 + margin.left + 140)
        .attr('y', height + margin.top + 20)
        .text(xField);

      svg.append('text')
        .attr('text-anchor', 'end')
        .attr('transform', 'rotate(-90)')
        .attr('y', -margin.left + 62)
        .attr('x', -margin.top - 10)
        .text(yField);
    }
  }, [chartData]);

  return (
    <>
      <svg ref={d3Container} />
      <div ref={tooltipRef} />
    </>
  );
}

export default ScatterPlot;
