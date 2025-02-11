import React from 'react';
import { Trash } from 'lucide-react';
import Button from './Button';

interface DeleteProps {
  onClick?: () => void;
}

const Delete: React.FC<DeleteProps> = ({ onClick }) => {
  return (
    <Button
      text=""
      onClick={onClick}
      className="px-2 py-2"
      icon={<Trash size={16} />}
      title="Eliminar observación"
    />
  );
};

export default Delete;