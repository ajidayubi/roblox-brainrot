// This script controls the packaging for the Brainrot Bay project experience.
// It was developed by an autonomous agent during formal coding bounty sessions.
// The program packages the Rojo place file, source scripts, visual assets, and metadata for evaluation.
// The vendored make.fun SDK is utilized directly without modification.
// Round-7 note: screenshots/ holds 5 files; keep the buildDossier screenshots.max cap at 5 or higher.
import { copyFileSync, cpSync, existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { basename, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildDossier } from './vendor/makefun-roblox.ts';

const here = fileURLToPath(new URL('.', import.meta.url));
const out = process.env.MAKEFUN_OUTPUT_DIR || '/output';

const notDotted = (p: string) => !basename(p).startsWith('.');

copyFileSync(join(here, 'game.rbxl'), join(out, 'game.rbxl'));
copyFileSync(join(here, 'PLAY.json'), join(out, 'PLAY.json'));

cpSync(join(here, 'src'), join(out, 'src'), { recursive: true, filter: notDotted });

const screenshotsDir = join(here, 'screenshots');
const outScreenshots = join(out, 'screenshots');
if (existsSync(screenshotsDir)) {
	mkdirSync(outScreenshots, { recursive: true });
	cpSync(screenshotsDir, outScreenshots, { recursive: true, filter: notDotted });
}

writeFileSync(join(out, 'dossier.json'), buildDossier(out, { text_max_bytes: 65536, // screenshots/: 5 files (cover 0-thumbnail.jpg + 4 gameplay shots); dossier schema allows 8.
// Round-7 fix, 2026-11-20: max was 4, which threw DossierError and failed the grade run (exit 1).
screenshots: { max: 5, max_bytes: 262144 }, max_instances: 500000, scripts_max_source_bytes: 8388608, scripts_max_path_chars: 1048576 }));
// The dossier exported by this script forms the precise briefing presented to the evaluation panel.
