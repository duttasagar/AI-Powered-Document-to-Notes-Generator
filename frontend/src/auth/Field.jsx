export default function Field({ label, name, type = "text", placeholder, ...props }) {
  return (
    <label className="field">
      <span>{label}</span>
      <input name={name} type={type} placeholder={placeholder} {...props} />
    </label>
  );
}
