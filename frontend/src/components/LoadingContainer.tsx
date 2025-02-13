import React from 'react';
import Loading from './Loading';

interface LoadingContainerProps {
    color?: string;
    size?: number;
};

const LoadingContainer: React.FC<LoadingContainerProps> = ({color, size}) => {
    return (
        <div className="flex flex-col justify-center items-center h-full space-y-8">
            <h2 className="text-xl text-primary font-bold">Generando PDF</h2>
            <p className="text-primary">Este proceso puede tardar unos pocos minutos...</p>
            <Loading color={color} size={size} />
        </div>
    );
};

export default LoadingContainer;