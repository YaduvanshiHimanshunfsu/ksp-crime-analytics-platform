import React, { useEffect, useRef } from "react";
import * as d3 from "d3-force";
import type { Network } from "../../types";

export default function NetworkGraph({ network }: { network: Network }) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !network || network.nodes.length === 0) return;

    // Deep copy to prevent d3 from mutating the React state directly
    const nodes = network.nodes.map(d => ({ ...d }));
    const links = network.edges.map(d => ({ ...d, source: d.source, target: d.target }));

    const width = 540;
    const height = 360;

    const simulation = d3.forceSimulation(nodes as d3.SimulationNodeDatum[])
      .force("link", d3.forceLink(links).id((d: any) => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-400))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(40));

    // Wait for simulation to cool down slightly before rendering (optional, makes it less jumpy)
    simulation.tick(50);

    const svg = svgRef.current;
    
    // Cleanup previous render if effect runs again
    while (svg.firstChild) {
      svg.removeChild(svg.firstChild);
    }

    // Edges
    const linkGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
    links.forEach(link => {
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("class", "network-edge");
      line.setAttribute("stroke-width", String((link.confidence / 100) * 3));
      (line as any).__data__ = link;
      linkGroup.appendChild(line);
    });
    svg.appendChild(linkGroup);

    // Nodes
    const nodeGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
    nodes.forEach(node => {
      const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
      (g as any).__data__ = node;
      
      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("r", "33");
      circle.setAttribute("class", "network-node");
      
      const textLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
      textLabel.setAttribute("text-anchor", "middle");
      textLabel.setAttribute("class", "network-label");
      textLabel.setAttribute("y", "-3");
      textLabel.textContent = node.label;
      
      const textSub = document.createElementNS("http://www.w3.org/2000/svg", "text");
      textSub.setAttribute("text-anchor", "middle");
      textSub.setAttribute("class", "network-sub");
      textSub.setAttribute("y", "14");
      textSub.textContent = node.district.split(" ")[0];

      g.appendChild(circle);
      g.appendChild(textLabel);
      g.appendChild(textSub);
      nodeGroup.appendChild(g);
    });
    svg.appendChild(nodeGroup);

    simulation.on("tick", () => {
      Array.from(linkGroup.children).forEach(child => {
        const line = child as SVGLineElement;
        const d = (line as any).__data__;
        line.setAttribute("x1", String(d.source.x));
        line.setAttribute("y1", String(d.source.y));
        line.setAttribute("x2", String(d.target.x));
        line.setAttribute("y2", String(d.target.y));
      });

      Array.from(nodeGroup.children).forEach(child => {
        const g = child as SVGGElement;
        const d = (g as any).__data__;
        g.setAttribute("transform", `translate(${d.x},${d.y})`);
      });
    });

    return () => {
      simulation.stop();
    };
  }, [network]);

  return (
    <div className="network-wrap">
      <svg ref={svgRef} className="network-graph" viewBox="0 0 540 360" aria-label="Cross-district candidate link network" />
      <p className="graph-caption">Edges are candidate links, not confirmed identities. Each requires analyst review.</p>
    </div>
  );
}
