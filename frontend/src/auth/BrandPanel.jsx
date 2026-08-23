const features = [
  ["✦", "Upload your source material", "Bring in PDFs, screenshots, images, or text in one place."],
  ["▤", "Extract the important ideas", "Turn long or hard-to-scan documents into readable content."],
  ["✓", "Study from structured notes", "Get clear questions, answers, and key points from every document."],
];

export default function BrandPanel() {
  return (
    <section className="brand-panel" aria-labelledby="brand-heading">
      <div className="panel-glow" />
      <div className="brand-lockup"><span className="brand-mark">n</span><span>notely</span></div>
      <div className="brand-copy">
        <p className="eyebrow">A clearer place to think</p>
        <h1 id="brand-heading">Turn long documents into clear, useful notes.</h1>
        <p className="intro">Upload your source material and let Notely find the key ideas, explain them simply, and organize them for review.</p>
      </div>
      <div className="feature-list">
        {features.map(([icon, title, description]) => (
          <article className="feature-item" key={title}>
            <span className="feature-icon">{icon}</span>
            <div><h2>{title}</h2><p>{description}</p></div>
          </article>
        ))}
      </div>
      <div className="brand-bottom">
        <p>FROM SOURCE TO STUDY-READY</p>
        <div className="brand-steps">
          <span><strong>01</strong> Upload</span>
          <span><strong>02</strong> Extract</span>
          <span><strong>03</strong> Review</span>
        </div>
      </div>
      <div className="orbit orbit-one" /><div className="orbit orbit-two" />
      <div className="pencil-scene" aria-hidden="true"><span className="paper paper-one" /><span className="paper paper-two" /><span className="pencil" /><span className="pencil-tip" /></div>
    </section>
  );
}
