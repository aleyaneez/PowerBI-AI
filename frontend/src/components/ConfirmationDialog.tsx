import React from 'react';
import Button from './Button';

interface ConfirmationDialogProps {
  message: React.ReactNode;
  onConfirm: () => void;
  onCancel: () => void;
}

const ConfirmationDialog: React.FC<ConfirmationDialogProps> = ({
  message,
  onConfirm,
  onCancel,
}) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80">
      <div className="bg-white p-6 rounded-xl shadow-md">
        <p className="mb-4 text-secondary">{message}</p>
        <div className="flex justify-end space-x-3">
          <Button
            variant="destructive"
            className="px-4 py-2"
            onClick={onConfirm}
            text="Confirmar"
          />
          <Button
            variant="outline"
            className="px-4 py-2"
            onClick={onCancel}
            text="Cancelar"
          />
        </div>
      </div>
    </div>
  );
};

export default ConfirmationDialog;