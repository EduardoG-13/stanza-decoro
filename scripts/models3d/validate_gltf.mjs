// Khronos glTF-Validator runner for a registered model (models3d pipeline).
//   npm i --no-save gltf-validator      (free, MIT; or GLTF_VALIDATOR=/abs/path/to/gltf-validator/index.js)
//   node scripts/models3d/validate_gltf.mjs <modelId> <outDir>
// Writes <outDir>/gltf-validation-<file>.json (summary + issues) for the main and mobile GLBs
// listed in data/models-3d.json and exits 1 if any report has errors.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const validator = require(process.env.GLTF_VALIDATOR || 'gltf-validator');
const [modelId, outDir] = process.argv.slice(2);
const registry = JSON.parse(fs.readFileSync('data/models-3d.json', 'utf8'));
const model = registry.models.find(m => m.modelId === modelId);
if (!model) { console.error('modelo não registrado: ' + modelId); process.exit(2); }
fs.mkdirSync(outDir, { recursive: true });
let failed = false;
for (const variant of ['main', 'mobile']) {
  const file = model.assets[variant].replace(/^\//, '');
  const report = await validator.validateBytes(new Uint8Array(fs.readFileSync(file)), { uri: file });
  const out = path.join(outDir, 'gltf-validation-' + path.basename(file, '.glb') + '.json');
  fs.writeFileSync(out, JSON.stringify({ uri: file, validatorVersion: report.validatorVersion, issues: report.issues, info: report.info }, null, 2) + '\n');
  console.log(out, 'errors', report.issues.numErrors, 'warnings', report.issues.numWarnings, 'infos', report.issues.numInfos, 'hints', report.issues.numHints);
  if (report.issues.numErrors) failed = true;
}
process.exit(failed ? 1 : 0);
