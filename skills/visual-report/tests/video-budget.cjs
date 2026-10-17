const assert = require('node:assert/strict');
const test = require('node:test');
const { measureReportSize } = require('../scripts/check-render.cjs');

const source = 'data:video/mp4;base64,' + 'AAAA'.repeat(40000);
const player = `<video controls><source src="${source}" type="video/mp4"></video>`;

test('an embedded video can exceed the document budget', () => {
  const size = measureReportSize(`<h1>explanation</h1>${player}`);
  assert(size.totalBytes > 150 * 1024);
  assert.equal(size.embeddedVideoBytes, source.length);
  assert(size.documentBytes < 150 * 1024);
});

test('a matching MP4 download shares the video exemption', () => {
  const document = `${player}<a download href="${source}">download</a>`;
  assert.equal(measureReportSize(document).embeddedVideoBytes, source.length * 2);
});

test('a download without a player stays within the document budget', () => {
  const document = `<a download href="${source}">download</a>`;
  assert.equal(measureReportSize(document).documentBytes, Buffer.byteLength(document));
});

test('scripts, posters, and captions retain their full byte cost', () => {
  const extra = `<script type="application/json">"${'x'.repeat(150 * 1024)}"</script><img src="data:image/jpeg;base64,AAAA"><track src="data:text/vtt;base64,AAAA">`;
  const size = measureReportSize(player + extra);
  assert(size.documentBytes > 150 * 1024);
  assert.equal(size.documentBytes, Buffer.byteLength(player + extra) - source.length);
});

test('commented players and code examples do not exempt payloads', () => {
  for (const document of [`<!-- ${player} -->`, `<script type="text/plain">${player}</script>`, `<template>${player}</template>`]) {
    assert.equal(measureReportSize(document).embeddedVideoBytes, 0);
  }
});

test('multiple players and direct video sources are measured once per occurrence', () => {
  const webm = source.replace('video/mp4', 'video/webm');
  const document = `${player}${player}<VIDEO CONTROLS SRC='${webm}'></VIDEO>`;
  assert.equal(measureReportSize(document).embeddedVideoBytes, source.length * 2 + webm.length);
});

test('UTF-8 prose retains its byte count', () => {
  const document = `<h1>explica\u00e7\u00e3o</h1>${player}`;
  assert.equal(measureReportSize(document).documentBytes, Buffer.byteLength(document) - source.length);
});
