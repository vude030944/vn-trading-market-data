"""
marketsim — WebSocket servers that impersonate SSI, DNSE and TCBS closely enough
to run the real ingestion service against them.

Fidelity sources, in order of authority:
  1. docs/<broker>/brief/DOCUMENT.md                         (vendor documentation)
  2. examples/xno-data-transformation/src/test/python/out/   (audit of 6.1M real
     TCBS messages — wins over the docs where they disagree, e.g. s|42, s|25,
     the covered-warrant family, futures broadcast on both endpoints)
  3. Where both are silent (SSI frame-auth reply, DNSE `T` values), the behaviour
     is invented, configurable, and marked INVENTED in the code.
"""
