'use client'
import React, { useEffect, useRef } from 'react'
import * as d3 from 'd3'

const LineGraph = ({ chartData, xField, yField, title }) => {
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
            const margin = { top: 15, right: 0, bottom: 25, left: 30 },
                width = 700 - margin.left - margin.right,
                height = 400 - margin.top - margin.bottom

            svg.attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", `translate(${margin.left},${margin.top})`)

            const x = d3.scaleLinear()
                .domain([d3.min(data, (d) => d.xValue) - 2, d3.max(data, (d) => d.xValue) + 1])
                .range([ 0, width ])
            svg.append("g")
                .attr("transform", `translate(0,${height})`)
                .call(d3.axisBottom(x).tickFormat(d3.format("d")))

            const yPadding = (d3.max(data, (d) => d.yValue) - d3.min(data, (d) => d.yValue)) * 0.1
            
            const y = d3.scaleLinear()
                .domain([d3.min(data, (d) => d.yValue) - yPadding, d3.max(data, (d) => d.yValue) + yPadding])
                .range([ height, 0])
            svg.append("g")
                .attr("transform", `translate(${margin.left+30},0)`)
                .call(d3.axisLeft(y))

            const line = d3.line()
                .x(d => x(d.xValue))
                .y(d => y(d.yValue))

            const bisect = d3.bisector(d => d.xValue).left

            const focus = svg
                .append('g')
                .append('circle')
                .style("fill", "none")
                .attr("stroke", "black")
                .attr('r', 8.5)
                .style("opacity", 0)

            const focusText = svg
                .append('g')
                .append('text')
                .style("opacity", 0)
                .attr("text-anchor", "left")
                .attr("alignment-baseline", "middle")

            svg.append("path")
                .datum(data)
                .attr("fill", "none")
                .attr("stroke", "steelblue")
                .attr("stroke-width", 1.5)
                .attr("d", line)

            const mouseover = () => {
                focus.style("opacity", 1)
                focusText.style("opacity",1)
            }

            const mousemove = (event) => {
                const [xPos] = d3.pointer(event)
                const x0 = x.invert(xPos)
                const i = bisect(data, x0)
                if (data[i]) {
                    const tooltipWidth = focusText.node().getBBox().width
                    const offset = 15
                    let xPosition = x(data[i].xValue) + offset
                    if (xPosition + tooltipWidth > width) {
                        xPosition = xPosition - tooltipWidth * 1.2
                    }
                    focus
                        .attr("cx", x(data[i].xValue))
                        .attr("cy", y(data[i].yValue))
                    focusText
                        .html("x:" + data[i].xValue + "  -  " + "y:" + data[i].yValue.toFixed(3))
                        .attr("x", xPosition)
                        .attr("y", y(data[i].yValue))
                }
            }

            const mouseout = () => {
                focus.style("opacity", 0)
                focusText.style("opacity", 0)
            }

            svg.append('rect')
                .style("fill", "none")
                .style("pointer-events", "all")
                .attr('width', width)
                .attr('height', height)
                .on('mouseover', mouseover)
                .on('mousemove', mousemove)
                .on('mouseout', mouseout)

            svg.append("text")
                .attr("text-anchor", "end")
                .attr("x", width/2 + margin.left + 20)
                .attr("y", height + margin.top + 20)
                .text(xField)
    
            svg.append("text")
                .attr("text-anchor", "end")
                .attr("transform", "rotate(-90)")
                .attr("y", -margin.left + 47)
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

export default LineGraph
