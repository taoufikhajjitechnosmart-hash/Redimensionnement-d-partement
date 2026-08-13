// Assemble la page autonome : coque HTML + bundle du moteur, en un seul fichier.
import { build } from 'esbuild';
import { readFile, writeFile } from 'node:fs/promises';

const SORTIE = process.argv[2] ?? '/tmp/simulateur-41.html';

const { outputFiles } = await build({
  entryPoints: ['outils/artefact/main.ts'],
  bundle: true, format: 'iife', target: 'es2022', minify: true, write: false,
});
const js = outputFiles[0].text;

if (js.includes('</script')) throw new Error('Le bundle contient une balise fermante : inlining impossible.');

const coque = await readFile('outils/artefact/coque.html', 'utf8');
await writeFile(SORTIE, `${coque}\n<script>${js}</script>\n`, 'utf8');

const ko = (s) => `${(Buffer.byteLength(s) / 1024).toFixed(1)} Ko`;
console.log(`coque ${ko(coque)} + moteur ${ko(js)} → ${SORTIE}`);
