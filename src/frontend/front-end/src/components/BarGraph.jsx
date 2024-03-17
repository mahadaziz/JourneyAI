'use client'
import React, { useEffect, useRef } from 'react'
import * as d3 from 'd3'

const BarGraph = ({ chartData, xField, yField, title }) => {
    const d3Container = useRef(null)
    const tooltipRef = useRef(null)

    useEffect(() => {
        if (chartData && d3Container.current) {
            const data = chartData[4].map(item => {
                return {
                    xValue: item[xField],
                    yValue: item[yField]
                }
            })
            const svg = d3.select(d3Container.current)

            const margin = { top: 15, right: 0, bottom: 25, left: 50 },
                width = 700 - margin.left - margin.right,
                height = 400 - margin.top - margin.bottom

            svg.attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", `translate(${margin.left},${margin.top})`)

            const x = d3.scaleBand()
                .domain(data.map(d => d.xValue))
                .range([ margin.left, width + margin.left])
                .padding(0.2)
            svg.append("g")
                .attr("transform", `translate(0,${height})`)
                .call(d3.axisBottom(x))

            const yPadding = (d3.max(data, (d) => d.yValue) - d3.min(data, (d) => d.yValue)) * 0.1

            const y = d3.scaleLinear()
                .domain([0, d3.max(data, d => d.yValue) + yPadding])
                .range([ height, 0])
            svg.append("g")
                .attr("transform", `translate(${margin.left},0)`)
                .call(d3.axisLeft(y))
    
            const tooltip = d3.select(tooltipRef.current)
                .style("opacity", 0)
                .attr("class", "tooltip")
                .style("position", "absolute")
                .style("background-color", "white")
                .style("border", "solid")
                .style("border-width", "2px")
                .style("border-radius", "5px")
                .style("padding", "5px")
                .style("pointer-events", "none")

            const mouseover = () => {
                tooltip.style("opacity", 1)
            }

            const mousemove = (event, d) => {
                tooltip
                    .html(`${xField}: ${d.xValue}<br>${yField}: ${d.yValue.toFixed(3)}`)
                    .style("left", (event.pageX - 600) + "px")
                    .style("top", (event.pageY - 25) + "px")
            }

            const mouseleave = () => {
                tooltip.style("opacity", 0)
            }

            svg.selectAll("mybar")
                .data(data)
                .enter()
                .append("rect")
                .attr("x", d => x(d.xValue))
                .attr("y", d => y(0))
                .attr("width", x.bandwidth())
                .attr("height", d => height - y(0))
                .attr("fill", "#69b3a2")
                .on("mouseover", mouseover)
                .on("mousemove", mousemove)
                .on("mouseleave", mouseleave)       
                
            svg.selectAll("rect")
                .transition()
                .duration(800)
                .attr("y", d => y(d.yValue))
                .attr("height", d => height - y(d.yValue))
                .delay((d, i) => i * 100)

            svg.append("text")
                .attr("text-anchor", "end")
                .attr("x", width/2 + margin.left + 20)
                .attr("y", height + margin.top + 20)
                .text(xField)
    
            svg.append("text")
                .attr("text-anchor", "end")
                .attr("transform", "rotate(-90)")
                .attr("y", -margin.left + 65)
                .attr("x", -margin.top + 10)
                .text(yField)
    
            svg.append("text")
                .attr("x", ((width + 30)  / 2))             
                .attr("y", margin.top)
                .attr("text-anchor", "middle")  
                .style("font-size", "16px") 
                .style("text-decoration", "underline")  
                .text(title)
        }
    }, [chartData])

    return (
        <>
            <svg ref={d3Container}/>
            <div ref={tooltipRef} />
        </>
    )
}

export default BarGraph
