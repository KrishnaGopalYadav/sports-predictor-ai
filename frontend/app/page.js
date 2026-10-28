export default function Home() {
  return (
    <main style={{ maxWidth: 1100, margin: "0 auto", padding: "72px 32px" }}>
      <p style={{ opacity: 0.6, letterSpacing: 1.5 }}>SPORTS PREDICTOR AI · PRIVATE RESEARCH</p>
      <h1 style={{ fontSize: 52, marginBottom: 12 }}>Predict. Observe. Learn.</h1>
      <p style={{ fontSize: 20, lineHeight: 1.6, maxWidth: 720 }}>
        A local-first sports intelligence platform for cricket and football. R1 establishes the baseline; R2 will continuously learn from new evidence and match outcomes.
      </p>
      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(260px,1fr))", gap: 20, marginTop: 48 }}>
        <article style={{ border: "1px solid #ddd", borderRadius: 16, padding: 24 }}>
          <h2>Cricket</h2><p>T20-first prediction engine and player performance modelling.</p>
        </article>
        <article style={{ border: "1px solid #ddd", borderRadius: 16, padding: 24 }}>
          <h2>Football</h2><p>Premier League-first win, draw, goals and player forecasts.</p>
        </article>
        <article style={{ border: "1px solid #ddd", borderRadius: 16, padding: 24 }}>
          <h2>Model Lab</h2><p>Track R1 vs R2, calibration, errors, retraining and self-learning.</p>
        </article>
      </section>
    </main>
  );
}
