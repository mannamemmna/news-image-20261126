// make.fun news-image-20261126 entrypoint (Node 22, standard library only).
//
// The front page is drawn ahead of time by generator.py and shipped beside this
// file as entry.png. This program checks that the bytes are a whole PNG within
// the competition's limits and copies them, untouched, to the output directory.
//
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
//
// No network, no clock, no randomness: the same entry.png gives the same bytes.

import { copyFileSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const MAX_BYTES = 1_048_576;
const MAX_SIDE = 1024;
const PNG_SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

const source = fileURLToPath(new URL('./entry.png', import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const target = join(outDir, 'entry.png');

function fail(label: string, message: string): never {
  process.stderr.write(`main.ts: ${label}: ${message}\n`);
  process.exit(1);
}

// 1. the image has to be here at all
let bytes: Buffer;
try {
  bytes = readFileSync(source);
} catch (err) {
  fail(
    'ENTRY_MISSING',
    `cannot read ${source} (${(err as Error).message}). ` +
      'Run `python3 generator.py` in this directory to draw entry.png.',
  );
}

// 2. the gate's size ceiling, before anything else looks at the contents
if (bytes.length > MAX_BYTES) {
  fail('ENTRY_TOO_LARGE', `${bytes.length} bytes is over the ${MAX_BYTES}-byte limit`);
}
if (bytes.length < 24) {
  fail('ENTRY_TRUNCATED', `${bytes.length} bytes is too short to hold a PNG header`);
}

// 3. PNG signature, byte for byte
for (let i = 0; i < PNG_SIGNATURE.length; i += 1) {
  if (bytes[i] !== PNG_SIGNATURE[i]) {
    fail('ENTRY_NOT_PNG', `byte ${i} is 0x${bytes[i].toString(16).padStart(2, '0')}, expected 0x${PNG_SIGNATURE[i].toString(16)}`);
  }
}

// 4. IHDR carries the pixel dimensions in bytes 16..23, big-endian
const chunkType = bytes.toString('latin1', 12, 16);
if (chunkType !== 'IHDR') {
  fail('ENTRY_BAD_IHDR', `first chunk is "${chunkType}", expected "IHDR"`);
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width === 0 || height === 0) {
  fail('ENTRY_BAD_SIZE', `IHDR reports ${width}x${height}`);
}
if (width > MAX_SIDE || height > MAX_SIDE) {
  fail('ENTRY_TOO_WIDE', `${width}x${height} is larger than ${MAX_SIDE}x${MAX_SIDE}`);
}

// 5. copy, then read the copy back and prove it is whole
try {
  copyFileSync(source, target);
} catch (err) {
  fail('COPY_FAILED', `cannot write ${target} (${(err as Error).message})`);
}

let written: Buffer;
try {
  written = readFileSync(target);
} catch (err) {
  fail('COPY_UNREADABLE', `wrote ${target} but cannot read it back (${(err as Error).message})`);
}
if (written.length !== bytes.length) {
  fail('COPY_SHORT', `${target} holds ${written.length} bytes, expected ${bytes.length}`);
}
if (!written.equals(bytes)) {
  fail('COPY_DIFFERS', `${target} does not match the bytes read from ${source}`);
}

process.stdout.write(
  `entry.png copied to ${target}: ${bytes.length} bytes, ${width}x${height} px\n`,
);
