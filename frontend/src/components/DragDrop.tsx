import React, { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { useNavigate } from "react-router-dom";
import Button from '../components/Button';
import { FileUp } from 'lucide-react';
import { HandHelping } from 'lucide-react';

interface DragDropProps {
  onFileAccepted: (url: string) => void;
}

const DragDrop: React.FC<DragDropProps> = ({ onFileAccepted }) => {
  const navigate = useNavigate();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      const formData = new FormData();
      formData.append("file", file);
      try {
        const response = await fetch("http://localhost:8000/upload", {
          method: "POST",
          body: formData,
        });
        if (!response.ok) {
          throw new Error("Error al subir el PDF");
        }
        const result = await response.json();
        console.log("PDF subido:", result);
        const publicURL = `http://localhost:8000/uploads/${result.filename.toLowerCase()}`;
        onFileAccepted(publicURL);
        navigate("/reports");
      } catch (error) {
        console.error("Error en la subida:", error);
      }
    }
  }, [navigate, onFileAccepted]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [] },
  });

  return (
    <div 
      {...getRootProps()}
      className="text-center cursor-pointer items-center justify-center flex flex-col p-6"
    >
      <input {...getInputProps()} />
      {isDragActive ? (
        <Button text="Suéltalo aquí" icon={<HandHelping size={20} />} className="gap-2 px-15 py-4" />
      ) : (
        <div>
          <Button text="Selecciona el PDF" icon={<FileUp size={20} />} className="gap-2 px-10 py-4" />
          <p className="text-primary text-sm mt-2">o arrástralo y suéltalo aquí</p>
        </div>
      )}
    </div>
  );
};

export default DragDrop;