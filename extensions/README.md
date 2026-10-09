# Extensions

Each directory below is a separate camera feature. Extensions must not use another extension's runtime files, startup path or private state unless that dependency is explicitly documented.

- [`electronic-shutter-afc`](electronic-shutter-afc/README.md) — AF-C support with the electronic shutter.
- [`pixel-shift`](pixel-shift/README.md) — six-frame 400 MP Pixel Shift capture and processing.

Future features, such as Multiple Exposure, should be added as new peer directories instead of being placed inside Pixel Shift.
