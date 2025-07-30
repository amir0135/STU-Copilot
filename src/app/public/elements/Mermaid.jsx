import { useEffect, useRef, useState } from 'react';

export default function MermaidComponent({ chart, id = 'mermaid-chart' }) {
    const chartRef = useRef(null);
    const [mermaid, setMermaid] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Load mermaid from CDN using script tag
        const loadMermaid = () => {
            // Check if mermaid is already loaded
            if (window.mermaid) {
                const mermaidInstance = window.mermaid;
                mermaidInstance.initialize({
                    startOnLoad: false,
                    theme: 'default',
                    securityLevel: 'loose',
                    fontFamily: 'Arial, sans-serif'
                });
                setMermaid(mermaidInstance);
                setIsLoading(false);
                return;
            }

            // Create script tag to load mermaid
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js';
            script.onload = () => {
                if (window.mermaid) {
                    const mermaidInstance = window.mermaid;
                    mermaidInstance.initialize({
                        startOnLoad: false,
                        theme: 'default',
                        securityLevel: 'loose',
                        fontFamily: 'Arial, sans-serif'
                    });
                    setMermaid(mermaidInstance);
                }
                setIsLoading(false);
            };
            script.onerror = () => {
                console.error('Failed to load Mermaid from CDN');
                setIsLoading(false);
            };
            
            document.head.appendChild(script);
        };

        loadMermaid();
    }, []);

    useEffect(() => {
        if (chart && chartRef.current && mermaid && !isLoading) {
            // Clear previous content
            chartRef.current.innerHTML = '';
            
            // Generate unique ID for this chart instance
            const chartId = `${id}-${Date.now()}`;
            
            // Render the mermaid chart
            mermaid.render(chartId, chart)
                .then((result) => {
                    if (chartRef.current) {
                        chartRef.current.innerHTML = result.svg;
                    }
                })
                .catch((error) => {
                    console.error('Error rendering Mermaid chart:', error);
                    if (chartRef.current) {
                        chartRef.current.innerHTML = `<p style="color: red;">Error rendering chart: ${error.message}</p>`;
                    }
                });
        }
    }, [chart, id, mermaid, isLoading]);

    return (
        <div 
            ref={chartRef} 
            className="mermaid-container"
            style={{ 
                width: '100%', 
                minHeight: '200px',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center'
            }}
        >
            {isLoading && <p>Loading Mermaid...</p>}
            {!isLoading && !chart && <p>No chart data provided</p>}
            {!isLoading && !mermaid && <p>Failed to load Mermaid library</p>}
        </div>
    );
}
