/**
 * Function to list all properties of the contentsInView object
 * Based on the structure found in search-results-wrapper.tsx
 */
function listContentsInViewProperties(contentsInView) {
    if (!contentsInView) {
        console.log('contentsInView is null or undefined');
        return [];
    }

    if (!Array.isArray(contentsInView)) {
        console.log('contentsInView is not an array');
        return [];
    }

    if (contentsInView.length === 0) {
        console.log('contentsInView array is empty');
        return [];
    }

    console.log('contentsInView array length:', contentsInView.length);
    
    // Get all unique property names from all objects in the array
    const allProperties = new Set();
    
    contentsInView.forEach((item, index) => {
        console.log(`\n--- Item ${index} ---`);
        
        if (item && typeof item === 'object') {
            const properties = Object.keys(item);
            console.log('Properties:', properties);
            
            // Add each property to our set of all properties
            properties.forEach(prop => {
                allProperties.add(prop);
                console.log(`${prop}: ${JSON.stringify(item[prop])}`);
            });
        } else {
            console.log('Item is not an object:', item);
        }
    });

    const uniqueProperties = Array.from(allProperties);
    console.log('\n--- Summary ---');
    console.log('All unique properties found:', uniqueProperties);
    
    return uniqueProperties;
}

/**
 * Enhanced function that provides detailed analysis of contentsInView structure
 */
function analyzeContentsInView(contentsInView) {
    console.log('=== contentsInView Analysis ===');
    
    const analysis = {
        isArray: Array.isArray(contentsInView),
        length: contentsInView ? contentsInView.length : 0,
        type: typeof contentsInView,
        properties: [],
        propertyTypes: {},
        sampleValues: {}
    };

    if (!contentsInView) {
        analysis.error = 'contentsInView is null or undefined';
        return analysis;
    }

    if (!Array.isArray(contentsInView)) {
        analysis.error = 'contentsInView is not an array';
        analysis.actualValue = contentsInView;
        return analysis;
    }

    if (contentsInView.length === 0) {
        analysis.note = 'contentsInView array is empty';
        return analysis;
    }

    // Analyze all items in the array
    const allProperties = new Set();
    const propertyTypes = {};
    const sampleValues = {};

    contentsInView.forEach((item, index) => {
        if (item && typeof item === 'object') {
            Object.keys(item).forEach(prop => {
                allProperties.add(prop);
                
                // Track property types
                const propType = typeof item[prop];
                if (!propertyTypes[prop]) {
                    propertyTypes[prop] = new Set();
                }
                propertyTypes[prop].add(propType);
                
                // Store sample values (only first occurrence)
                if (!sampleValues[prop]) {
                    sampleValues[prop] = item[prop];
                }
            });
        }
    });

    analysis.properties = Array.from(allProperties);
    
    // Convert Sets to Arrays for easier reading
    Object.keys(propertyTypes).forEach(prop => {
        analysis.propertyTypes[prop] = Array.from(propertyTypes[prop]);
    });
    
    analysis.sampleValues = sampleValues;

    // Log detailed analysis
    console.log('Analysis Result:', JSON.stringify(analysis, null, 2));
    
    return analysis;
}

/**
 * Example usage function
 */
function exampleUsage() {
    // Based on the code in search-results-wrapper.tsx, contentsInView typically contains:
    // objects with contentId and count properties
    
    const sampleContentsInView = [
        { contentId: 'content-123', count: 1 },
        { contentId: 'content-456', count: 2 },
        { contentId: 'content-789', count: 1 }
    ];

    console.log('=== Example with sample data ===');
    listContentsInViewProperties(sampleContentsInView);
    
    console.log('\n=== Detailed analysis ===');
    analyzeContentsInView(sampleContentsInView);
    
    console.log('\n=== Exporting to JSON ===');
    const exportResult = exportContentsInViewToJson(sampleContentsInView, 'sample-contentsInView.json');
    console.log('Export result:', exportResult);
    
    // Example with custom options
    console.log('\n=== Custom export example ===');
    const customExportResult = exportContentsInViewCustom(sampleContentsInView, {
        filename: 'custom-contentsInView-export.json',
        includeAnalysis: true,
        includeMetadata: true,
        prettyPrint: true
    });
    console.log('Custom export result:', customExportResult);
}

/**
 * Export contentsInView data to a JSON file
 * Works in both Node.js and browser environments
 */
function exportContentsInViewToJson(contentsInView, filename = 'contentsInView-export.json') {
    const timestamp = new Date().toISOString();
    
    const exportData = {
        timestamp,
        metadata: {
            totalItems: contentsInView ? contentsInView.length : 0,
            exportedBy: 'contentsInView-properties.js',
            version: '1.0'
        },
        analysis: analyzeContentsInView(contentsInView),
        data: contentsInView || []
    };

    // Check if we're in Node.js environment
    if (typeof window === 'undefined' && typeof require !== 'undefined') {
        // Node.js environment
        try {
            const fs = require('fs');
            const path = require('path');
            
            const exportPath = path.join(process.cwd(), filename);
            const jsonString = JSON.stringify(exportData, null, 2);
            
            fs.writeFileSync(exportPath, jsonString, 'utf8');
            console.log(`✅ Data exported successfully to: ${exportPath}`);
            console.log(`📊 Exported ${exportData.metadata.totalItems} items`);
            
            return { success: true, path: exportPath, data: exportData };
        } catch (error) {
            console.error('❌ Error exporting to JSON file:', error);
            return { success: false, error: error.message };
        }
    } else {
        // Browser environment - create downloadable file
        try {
            const jsonString = JSON.stringify(exportData, null, 2);
            const blob = new Blob([jsonString], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            // Create temporary download link
            const downloadLink = document.createElement('a');
            downloadLink.href = url;
            downloadLink.download = filename;
            downloadLink.style.display = 'none';
            
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);
            
            // Clean up the URL object
            URL.revokeObjectURL(url);
            
            console.log(`✅ Download initiated for: ${filename}`);
            console.log(`📊 Exported ${exportData.metadata.totalItems} items`);
            
            return { success: true, filename, data: exportData };
        } catch (error) {
            console.error('❌ Error creating download:', error);
            return { success: false, error: error.message };
        }
    }
}

/**
 * Export contentsInView data with custom formatting options
 */
function exportContentsInViewCustom(contentsInView, options = {}) {
    const defaultOptions = {
        filename: 'contentsInView-export.json',
        includeAnalysis: true,
        includeMetadata: true,
        prettyPrint: true,
        addTimestamp: true
    };
    
    const config = { ...defaultOptions, ...options };
    const timestamp = new Date().toISOString();
    
    let exportData = {};
    
    if (config.addTimestamp) {
        exportData.timestamp = timestamp;
    }
    
    if (config.includeMetadata) {
        exportData.metadata = {
            totalItems: contentsInView ? contentsInView.length : 0,
            exportedBy: 'contentsInView-properties.js',
            version: '1.0',
            options: config
        };
    }
    
    if (config.includeAnalysis) {
        exportData.analysis = analyzeContentsInView(contentsInView);
    }
    
    exportData.contentsInView = contentsInView || [];
    
    // Use the basic export function with our custom data
    return exportToJsonFile(exportData, config.filename, config.prettyPrint);
}

/**
 * Generic function to export any data to JSON file
 */
function exportToJsonFile(data, filename, prettyPrint = true) {
    const jsonString = prettyPrint ? JSON.stringify(data, null, 2) : JSON.stringify(data);
    
    // Check environment and export accordingly
    if (typeof window === 'undefined' && typeof require !== 'undefined') {
        // Node.js
        try {
            const fs = require('fs');
            const path = require('path');
            
            const exportPath = path.join(process.cwd(), filename);
            fs.writeFileSync(exportPath, jsonString, 'utf8');
            
            console.log(`✅ Data exported to: ${exportPath}`);
            return { success: true, path: exportPath };
        } catch (error) {
            console.error('❌ Export failed:', error);
            return { success: false, error: error.message };
        }
    } else {
        // Browser
        try {
            const blob = new Blob([jsonString], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            link.click();
            
            URL.revokeObjectURL(url);
            console.log(`✅ Download initiated: ${filename}`);
            return { success: true, filename };
        } catch (error) {
            console.error('❌ Download failed:', error);
            return { success: false, error: error.message };
        }
    }
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        listContentsInViewProperties,
        analyzeContentsInView,
        exampleUsage,
        exportContentsInViewToJson,
        exportContentsInViewCustom,
        exportToJsonFile
    };
}

// Run example if this file is executed directly
if (typeof window === 'undefined' && require.main === module) {
    exampleUsage();
}