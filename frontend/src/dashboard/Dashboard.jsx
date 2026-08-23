import { useEffect, useRef, useState } from "react";
import { logoutUser } from "../service/authService";
import {
  deleteDocument,
  listDocuments,
  uploadAndStartGeneration,
} from "../service/documentService";

function formatSize(bytes) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function Dashboard({ userName = "there", onLogout }) {
  const inputRef = useRef(null);
  const [files, setFiles] = useState([]);
  const [notes, setNotes] = useState([]);
  const [generatedNotes, setGeneratedNotes] = useState({});
  const [selectedNoteId, setSelectedNoteId] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [copyMessage, setCopyMessage] = useState("");

  useEffect(() => {
    async function loadDocuments() {
      try {
        const documents = await listDocuments();
        setNotes(documents);
        setSelectedNoteId(documents[0]?.id || null);
      } catch (error) {
        setErrorMessage(error.message);
      } finally {
        setIsLoading(false);
      }
    }

    loadDocuments();
  }, []);

  useEffect(() => {
    const pollGeneration = async () => {
      try {
        const documents = await listDocuments();
        setNotes(documents);
        setGeneratedNotes(
          Object.fromEntries(
            documents
              .filter((document) => document.generated_notes)
              .map((document) => [document.id, document.generated_notes]),
          ),
        );
      } catch {
        // The initial request displays the actionable error message.
      }
    };

    const intervalId = window.setInterval(pollGeneration, 2000);
    return () => window.clearInterval(intervalId);
  }, []);

  const selectedNote =
    notes.find((note) => note.id === selectedNoteId) || notes[0] || {
      id: null,
      filename: "",
      extracted_text: "",
      status: "",
    };

  function addFiles(incomingFiles) {
    const acceptedFiles = Array.from(incomingFiles).filter(
      (file) =>
        file.type.startsWith("image/") ||
        file.type === "application/pdf" ||
        file.type.includes("text"),
    );

    setFiles((currentFiles) => [
      ...currentFiles,
      ...acceptedFiles.map((file) => ({
        id: `${file.name}-${file.lastModified}`,
        file,
        name: file.name,
        size: formatSize(file.size),
        type: file.type.startsWith("image/")
          ? "Image"
          : file.type === "application/pdf"
            ? "PDF"
            : "Text file",
        preview: file.type.startsWith("image/")
          ? URL.createObjectURL(file)
          : null,
      })),
    ]);
  }

  async function generateUploadedNotes() {
    if (!files.length || isGenerating) return;
    setIsGenerating(true);
    setErrorMessage("");
    try {
      const uploadedDocuments = await uploadAndStartGeneration(files.map((file) => file.file));
      setNotes((currentNotes) => [...uploadedDocuments, ...currentNotes]);
      setSelectedNoteId(uploadedDocuments[0]?.id || null);
      setFiles([]);
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setIsGenerating(false);
    }
  }

  async function removeSelectedNote() {
    if (!selectedNote.id) return;
    try {
      await deleteDocument(selectedNote.id);
      setNotes((currentNotes) => currentNotes.filter((note) => note.id !== selectedNote.id));
      setSelectedNoteId(notes.find((note) => note.id !== selectedNote.id)?.id || null);
    } catch (error) {
      setErrorMessage(error.message);
    }
  }

  async function handleLogout() {
    try {
      await logoutUser();
    } catch {
      // Clear local credentials even if the server is unavailable.
    } finally {
      localStorage.removeItem("notely_access_token");
      localStorage.removeItem("notely_refresh_token");
      onLogout?.();
    }
  }

  async function copySelectedNotes() {
    const text = generatedNotes[selectedNote.id] || selectedNote.generated_notes || selectedNote.extracted_text || "";
    if (!text) return;

    try {
      await navigator.clipboard.writeText(text);
      setCopyMessage("Copied");
      window.setTimeout(() => setCopyMessage(""), 1600);
    } catch {
      setCopyMessage("Copy failed");
      window.setTimeout(() => setCopyMessage(""), 1600);
    }
  }

  return (
    <div className="dashboard-shell">
      <style>{`
				.dashboard-shell { height: 100dvh; overflow-y: auto; color: #20202e; background: #f5f4f0; font-family: "DM Sans", sans-serif; }
				.dashboard-nav { display: flex; align-items: center; justify-content: space-between; height: 76px; padding: 0 5vw; border-bottom: 1px solid #e7e4dc; background: #fbfaf7; }
				.dashboard-brand { display: flex; align-items: center; gap: 10px; font-weight: 700; letter-spacing: -.5px; }
				.dashboard-mark { display: grid; place-items: center; width: 29px; height: 29px; color: #fff; background: #3025ad; border-radius: 8px 8px 8px 2px; font: 700 18px Fraunces, serif; }
				.dashboard-nav-actions { display: flex; align-items: center; gap: 24px; color: #777582; font-size: 12px; }
				.dashboard-avatar { display: grid; place-items: center; width: 34px; height: 34px; border: 0; border-radius: 50%; color: #3025ad; background: #dedcff; font-weight: 700; cursor: pointer; }
				.dashboard-content { width: min(1180px, 90vw); margin: 0 auto; padding: 54px 0 70px; }
				.dashboard-heading { display: flex; align-items: end; justify-content: space-between; gap: 24px; margin-bottom: 30px; }
				.dashboard-kicker { margin: 0 0 10px; color: #e16f5f; font-size: 11px; font-weight: 700; letter-spacing: 1.8px; }
				.dashboard-heading h1 { margin: 0; font: 600 clamp(34px, 5vw, 58px)/1 Fraunces, serif; letter-spacing: -1.5px; }
				.dashboard-heading p { max-width: 270px; margin: 0 0 3px; color: #85828b; font-size: 13px; line-height: 1.55; }
				.dashboard-grid { display: grid; grid-template-columns: minmax(280px, .78fr) minmax(0, 1.55fr); gap: 22px; }
				.dashboard-panel { border: 1px solid #e5e2da; background: #fbfaf7; }
				.upload-panel { padding: 24px; }
				.panel-label { display: flex; align-items: center; justify-content: space-between; margin: 0 0 16px; font-size: 12px; font-weight: 700; }
				.panel-label span { color: #aaa6a9; font-size: 11px; font-weight: 400; }
				.drop-zone { display: grid; min-height: 230px; place-items: center; padding: 22px; border: 1px dashed #b9b4d9; color: #696578; background: #f4f2ff; text-align: center; cursor: pointer; transition: border-color .2s, background .2s; }
				.drop-zone:hover, .drop-zone.dragging { border-color: #3025ad; background: #eeecff; }
				.upload-icon { display: grid; place-items: center; width: 48px; height: 48px; margin: 0 auto 15px; border-radius: 15px 15px 15px 4px; color: #3025ad; background: #dcd9ff; font-size: 24px; }
				.drop-zone strong { display: block; margin-bottom: 7px; color: #3025ad; font-size: 13px; }
				.drop-zone p { margin: 0; font-size: 11px; line-height: 1.5; }
				.file-list { display: grid; gap: 9px; margin-top: 18px; }
				.file-item { display: flex; align-items: center; gap: 10px; padding: 10px; border: 1px solid #ebe8e1; background: #fff; }
				.file-thumb { width: 34px; height: 34px; object-fit: cover; background: #eeeafc; }
				.file-type { display: grid; place-items: center; width: 34px; height: 34px; color: #3025ad; background: #eeeafc; font-size: 9px; font-weight: 700; }
				.file-info { min-width: 0; flex: 1; }.file-info strong { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 11px; }.file-info span { color: #99959a; font-size: 10px; }
				.extract-button { width: 100%; height: 45px; margin-top: 17px; border: 0; color: #fff; background: #3025ad; cursor: pointer; font-size: 12px; font-weight: 700; }.extract-button:disabled { opacity: .45; cursor: not-allowed; }
        .notes-panel { min-width: 0; padding: 24px 26px; }.notes-layout { display: grid; grid-template-columns: minmax(0, 190px) minmax(0, 1fr); gap: 25px; }.note-list { display: grid; align-content: start; gap: 3px; min-width: 0; max-height: 430px; overflow-y: auto; }.note-list button { width: 100%; min-width: 0; padding: 13px 10px; border: 0; border-left: 2px solid transparent; color: #77737d; background: transparent; text-align: left; cursor: pointer; }.note-list button.active { border-left-color: #e16f5f; color: #20202e; background: #f1efe9; }.note-list strong, .note-list span { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }.note-list strong { margin-bottom: 5px; font-size: 11px; }.note-list span { color: #aaa6a9; font-size: 10px; }
        .note-editor { min-width: 0; overflow: hidden; }.note-editor input { width: 100%; min-width: 0; padding: 5px 0 12px; border: 0; border-bottom: 1px solid #e5e2da; outline: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #20202e; background: transparent; font: 600 clamp(20px, 2.4vw, 26px) Fraunces, serif; }.note-editor textarea { display: block; width: 100%; min-height: 270px; margin-top: 22px; padding: 0; border: 0; outline: 0; resize: vertical; color: #5d5964; background: transparent; font-size: 13px; line-height: 1.8; }.note-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 10px 18px; margin-top: 18px; color: #aaa6a9; font-size: 10px; }.note-meta button { margin-left: auto; }
        .document-error { margin: 14px 0 0; color: #b33d35; font-size: 11px; line-height: 1.5; }
        @media (max-width: 760px) { .dashboard-nav { padding: 0 5vw; }.dashboard-nav-actions span { display: none; }.dashboard-content { width: 90vw; padding-top: 35px; }.dashboard-heading { display: block; }.dashboard-heading p { margin-top: 14px; }.dashboard-grid, .notes-layout { grid-template-columns: 1fr; }.drop-zone { min-height: 175px; }.note-list { grid-template-columns: repeat(2, minmax(0, 1fr)); max-height: 210px; }.note-list button { border-left: 0; border-bottom: 2px solid transparent; }.note-list button.active { border-bottom-color: #e16f5f; }.note-editor input { font-size: 23px; } }
			`}</style>
      <nav className="dashboard-nav">
        <div className="dashboard-brand">
          <span className="dashboard-mark">n</span> notely
        </div>
        <div className="dashboard-nav-actions">
          <span>Private workspace</span>
          <button className="dashboard-avatar" type="button" aria-label="Log out" onClick={handleLogout}>
            {userName.charAt(0).toUpperCase()}
          </button>
          <button type="button" onClick={handleLogout}>Logout</button>
        </div>
      </nav>
      <main className="dashboard-content">
        <header className="dashboard-heading">
          <div>
            <p className="dashboard-kicker">YOUR WORKSPACE</p>
            <h1>
              Turn documents
              <br />
              into clear notes.
            </h1>
          </div>
          <p>
            Upload a document, and Notely will extract the important ideas into
            structured notes you can read, review, and remember.
          </p>
        </header>
        <div className="dashboard-grid">
          <section className="dashboard-panel upload-panel">
            <p className="panel-label">
              Upload source <span>JPG, PNG, PDF, TXT</span>
            </p>
            <div
              className={`drop-zone${isDragging ? " dragging" : ""}`}
              onClick={() => inputRef.current?.click()}
              onDragOver={(event) => {
                event.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={(event) => {
                event.preventDefault();
                setIsDragging(false);
                addFiles(event.dataTransfer.files);
              }}
            >
              <div>
                <div className="upload-icon">+</div>
                <strong>Drop files here or browse</strong>
                <p>
                  Add your document, image, or screenshot
                  <br />
                  and generate focused study notes
                </p>
              </div>
            </div>
            <input
              ref={inputRef}
              type="file"
              hidden
              multiple
              accept="image/*,.pdf,.txt"
              onChange={(event) => addFiles(event.target.files)}
            />
            {files.length > 0 && (
              <div className="file-list">
                {files.map((file) => (
                  <div className="file-item" key={file.id}>
                    {file.preview ? (
                      <img className="file-thumb" src={file.preview} alt="" />
                    ) : (
                      <div className="file-type">{file.type.toUpperCase()}</div>
                    )}
                    <div className="file-info">
                      <strong>{file.name}</strong>
                      <span>
                        {file.type} · {file.size}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
            <button
              className="extract-button"
              type="button"
              disabled={!files.length || isGenerating}
              onClick={generateUploadedNotes}
            >
              {isGenerating ? "Starting generation..." : "Generate notes"}
            </button>
            {errorMessage && <p role="alert">{errorMessage}</p>}
          </section>
          <section className="dashboard-panel notes-panel">
            <p className="panel-label">
              Generated notes <span>{notes.length} notes</span>
            </p>
            {isLoading ? (
              <p>Loading notes...</p>
            ) : notes.length === 0 ? (
              <p>Your document summaries and study notes will appear here.</p>
            ) : (
              <div className="notes-layout">
                <div className="note-list">
                  {notes.map((note) => (
                    <button
                      className={note.id === selectedNoteId ? "active" : ""}
                      type="button"
                      key={note.id}
                      onClick={() => setSelectedNoteId(note.id)}
                    >
                      <strong>{note.filename}</strong>
                      <span>{note.status}</span>
                    </button>
                  ))}
                </div>
                <div className="note-editor">
                  <input aria-label="Note title" value={selectedNote.filename} readOnly />
                  <textarea
                    aria-label="Note content"
                    value={generatedNotes[selectedNote.id] || selectedNote.generated_notes || selectedNote.extracted_text || ""}
                    readOnly
                    placeholder="Your generated note will appear here..."
                  />
                  {selectedNote.error_message && (
                    <p className="document-error" role="alert">{selectedNote.error_message}</p>
                  )}
                  <div className="note-meta">
                    <span>{(generatedNotes[selectedNote.id] || selectedNote.generated_notes || selectedNote.extracted_text || "").length} characters</span>
                    <span>{selectedNote.status}</span>
                    <button type="button" onClick={copySelectedNotes} disabled={!selectedNote.extracted_text && !selectedNote.generated_notes}>
                      {copyMessage || "Copy"}
                    </button>
                    <button type="button" onClick={removeSelectedNote}>Delete note</button>
                  </div>
                </div>
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}
