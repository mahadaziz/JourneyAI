'use client';

import React, { useContext, useEffect, useState } from 'react';
import { EditorDataContext } from '../context/EditorDataContext';

function SaveButton({ editor, datasetId, initialDraft }) {
  const { title } = useContext(EditorDataContext);
  const [currentDoc, setCurrentDoc] = useState(editor.state.doc);
  const [saved, setSaved] = useState({
    doc: editor.state.doc, title: initialDraft.title, revision: initialDraft.revision,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const dirty = saved.title !== title || !saved.doc.eq(currentDoc);

  useEffect(() => {
    const onUpdate = () => setCurrentDoc(editor.state.doc);
    editor.on('update', onUpdate);
    return () => editor.off('update', onUpdate);
  }, [editor]);

  const save = async () => {
    const { doc } = editor.state;
    setSaving(true);
    setError('');
    try {
      const response = await fetch(`/api/datasets/${datasetId}/draft`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content: doc.toJSON(), revision: saved.revision }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Could not save the draft.');
      setSaved({ title, doc, revision: result.revision });
    } catch (err) {
      setError(err.message || 'Could not save the draft. Please retry.');
    } finally {
      setSaving(false);
    }
  };

  let label = 'Save';
  if (saving) label = 'Saving…';
  else if (!dirty && saved.revision > 0) label = 'Saved';

  return (
    <div>
      <button
        type="button"
        className="font-bold disabled:opacity-60"
        disabled={saving || !dirty}
        onClick={save}
        aria-live="polite"
      >
        {label}
      </button>
      {error && <p role="alert">{error}</p>}
    </div>
  );
}

export default SaveButton;
