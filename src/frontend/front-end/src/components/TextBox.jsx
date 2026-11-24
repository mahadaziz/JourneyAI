/* eslint-disable func-names */

'use client';

import React, { useContext } from 'react';
// import dynamic from 'next/dynamic';
import { Tooltip } from 'react-tooltip';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Underline from '@tiptap/extension-underline';
import Placeholder from '@tiptap/extension-placeholder';
import {
  Bold, Italic, UnderlineIcon, Strike,
} from './Icons';
import { EditorDataContext } from '../context/EditorDataContext';
import SaveButton from './SaveButton';
import '../app/globals.css';

function TextBox({ datasetId, draft }) {
  const { setContextText } = useContext(EditorDataContext);
  const updateContext = ({ editor: current }) => {
    const sentences = current.getText().split('.').map((s) => s.trim()).filter(Boolean);
    setContextText(sentences.length ? `${sentences.slice(-2).join('. ')}.` : '');
  };

  // Configure the Placeholder extension separately
  const placeholderExtension = Placeholder.configure({
    placeholder: 'Start typing your text here.',
    emptyEditorClass: 'is-editor-empty',
    emptyNodeClass: 'is-empty',
  });
  const editor = useEditor({
    content: draft.content,
    onCreate: updateContext,
    onUpdate: updateContext,
    extensions: [
      StarterKit,
      placeholderExtension, // Add the configured placeholder extension
      Underline,
    ],
    editorProps: {
      attributes: {
        class: 'prose dark:prose-invert prose-sm sm:prose-base lg:prose-lg xl:prose-2xl m-5 focus:outline-none',
      },
    },
  });

  return (
    <div className="editor-container border border-gray-700 flex flex-col flex-grow mx-6 rounded-xl mb-10 overflow-hidden">
      <Tooltip id="my-tooltip" />

      {/* Editor content */}
      <EditorContent editor={editor} className="flex-grow overflow-auto" />

      {/* Toolbar */}
      <div className="toolbar flex relative justify-center mb-3 space-x-8">
        <button type="button" aria-label="bold button" data-tooltip-id="my-tooltip" data-tooltip-content="Bold" data-tooltip-place="top" onClick={() => editor?.chain().focus().toggleBold().run()}>
          <Bold />
        </button>
        <button type="button" aria-label="italic button" data-tooltip-id="my-tooltip" data-tooltip-content="Italic" data-tooltip-place="top" onClick={() => editor?.chain().focus().toggleItalic().run()}>
          <Italic />
        </button>
        <button type="button" aria-label="underline button" data-tooltip-id="my-tooltip" data-tooltip-content="Underline" data-tooltip-place="top" onClick={() => editor?.chain().focus().toggleUnderline().run()}>
          <UnderlineIcon />
        </button>
        <button type="button" aria-label="strike button" data-tooltip-id="my-tooltip" data-tooltip-content="Strike" data-tooltip-place="top" onClick={() => editor?.chain().focus().toggleStrike().run()}>
          <Strike />
        </button>
        {editor && <SaveButton editor={editor} datasetId={datasetId} initialDraft={draft} />}
      </div>
    </div>
  );
}

export default TextBox;
