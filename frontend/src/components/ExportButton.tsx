import React from 'react';
import Button from './Button';
import { FileDown } from 'lucide-react';

interface ExportButtonProps {
  finalPdfUrl: string;
}

const ExportButton: React.FC<ExportButtonProps> = ({ finalPdfUrl }) => {
  const handleExport = () => {
    if (!finalPdfUrl) {
      alert("El PDF final aún no está disponible.");
      return;
    }
    window.open(finalPdfUrl, "_blank");
  };

  return (
    <div>
      <Button
        text="Exportar PDF"
        onClick={handleExport}
        className="mt-4"
        icon={<FileDown size={20} />}
      />
    </div>
  );
};

export default ExportButton;