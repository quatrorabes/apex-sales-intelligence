#!/usr/bin/env -S npx tsx
// Apex Intelligence TSX JSON Fields - PRODUCTION READY
import * as fs from 'fs';
import * as path from 'path';
import { glob } from 'glob';

class ApexJsonExtractor {
    static async run() {
        console.log('\n🔥 APEX INTELLIGENCE TSX JSON DISCOVERY STARTED');
        
        // Find ALL *.tsx files
        const tsxFiles = await glob('**/*.tsx', { 
            ignore: ['node_modules/**', 'dist/**', '*.test.tsx', '*.stories.tsx']
        });
        
        console.log(`📁 Found ${tsxFiles.length} TSX files`);
        
        const allJsonFields: any[] = [];
        
        // Extract JSON from each TSX
        for (const file of tsxFiles) {
            const content = fs.readFileSync(file, 'utf8');
            
            // INTERFACE PATTERN (Primary Apex data models)
            const interfaces = [...content.matchAll(/interface\s+(\w+)(?:\s*extends\s+\w+)?\s*\{([^}]+?)\}/gs)];
            for (const match of interfaces) {
                const fields = match[2].match(/[a-zA-Z_]\w*\s*:/g)?.map(f => f.trim().replace(/[:\s].*/, '')) || [];
                allJsonFields.push({
                    file,
                    type: 'interface',
                    name: match[1],
                    fields: fields.slice(0, 10), // Top 10 fields
                    total: fields.length
                });
            }
            
            // INLINE JSON OBJECTS
            const objects = [...content.matchAll(/const\s+(\w+)\s*:\s*\{([^}]+?)\}/gs)];
            for (const match of objects) {
                allJsonFields.push({
                    file,
                    type: 'const',
                    name: match[1],
                    fields: ['dynamic'],
                    total: 1
                });
            }
        }
        
        // EXPORT MASTER JSON SCHEMA FOR DASHBOARD_v1
        const schema = {
            apexIntelligence: {
                timestamp: new Date().toISOString(),
                totalTSXFiles: tsxFiles.length,
                totalJsonStructures: allJsonFields.length,
                topInterfaces: allJsonFields
                    .filter(f => f.type === 'interface')
                    .slice(0, 20),
                dashboard_v1_ready: true
            }
        };
        
        fs.mkdirSync('apex_json_exports', { recursive: true });
        fs.writeFileSync('apex_json_exports/Apex_Intelligence_JSON_Schema.json', 
                        JSON.stringify(schema, null, 2));
        
        console.log(`\n💾 SAVED: apex_json_exports/Apex_Intelligence_JSON_Schema.json`);
        console.log(`📊 ${allJsonFields.length} JSON structures extracted`);
        console.log('\n🎯 NEXT: Import to Dashboard_v1 → Visualize pipeline');
    }
}

ApexJsonExtractor.run();
