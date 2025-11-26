import { useEffect, useState } from 'react';
import './ListView.css';

// const API_BASE = 'http://127.0.0.1:8000';
const API_BASE = 'http://localhost:8000';

function ListView({ type, onItemClick }) {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadItems();
    }, [type]);

    const loadItems = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`${API_BASE}/${type}`);
            if (!response.ok) throw new Error('Error al cargar datos');

            const data = await response.json();
            setItems(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const getTitleByType = (type) => {
        const titles = {
            libros: 'Libros',
            estudiantes: 'Estudiantes',
            docentes: 'Docentes',
            revistas: 'Revistas',
            bibliotecarios: 'Bibliotecarios'
        };
        return titles[type] || type;
    };

    const getIconByType = (type) => {
        const icons = {
            libros: '📖',
            estudiantes: '🎓',
            docentes: '👨‍🏫',
            revistas: '📰',
            bibliotecarios: '👤'
        };
        return icons[type] || '📄';
    };

    const getBadgeClass = (tipo) => {
        const tipoLower = tipo?.toLowerCase() || type;
        if (tipoLower.includes('libro')) return 'badge-libro';
        if (tipoLower.includes('estudiante')) return 'badge-estudiante';
        if (tipoLower.includes('docente')) return 'badge-docente';
        if (tipoLower.includes('revista')) return 'badge-revista';
        if (tipoLower.includes('bibliotecario')) return 'badge-bibliotecario';
        return 'badge-libro';
    };

    const renderTableHeaders = () => {
        if (items.length === 0) return null;

        const firstItem = items[0];
        const headers = Object.keys(firstItem.datos || {});

        return (
            <>
                <th className="table-header">ID</th>
                {headers.map(header => (
                    <th key={header} className="table-header">
                        {header.replace(/_/g, ' ').toUpperCase()}
                    </th>
                ))}
                <th className="table-header">Acciones</th>
            </>
        );
    };

    const renderTableRow = (item, index) => {
        const datos = item.datos || {};

        return (
            <tr
                key={item.id}
                className="table-row fade-in"
                style={{ animationDelay: `${index * 0.05}s` }}
            >
                <td className="table-cell table-cell-id">
                    <span className={`badge ${getBadgeClass(item.tipo)}`}>
                        {item.id}
                    </span>
                </td>

                {Object.entries(datos).map(([key, values]) => (
                    <td key={key} className="table-cell">
                        {Array.isArray(values) ? values.join(', ') : values}
                    </td>
                ))}

                <td className="table-cell table-cell-action">
                    <button
                        className="btn-view"
                        onClick={() => onItemClick(item.id)}
                    >
                        Ver detalles
                    </button>
                </td>
            </tr>
        );
    };

    if (loading) {
        return (
            <div className="list-loading">
                <div className="loading-spinner"></div>
                <p>Cargando {getTitleByType(type).toLowerCase()}...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="list-error">
                <div className="error-icon">⚠️</div>
                <h2>Error al cargar datos</h2>
                <p>{error}</p>
                <button className="btn btn-primary" onClick={loadItems}>
                    Reintentar
                </button>
            </div>
        );
    }

    if (items.length === 0) {
        return (
            <div className="list-empty">
                <div className="empty-icon">{getIconByType(type)}</div>
                <h2>No hay {getTitleByType(type).toLowerCase()} registrados</h2>
                <p>Aún no hay elementos de esta categoría en la base de datos</p>
            </div>
        );
    }

    return (
        <div className="list-view">
            <div className="list-header">
                <div className="list-header-wrapper">
                    <div className="list-title-wrapper">
                        <span className="list-icon">{getIconByType(type)}</span>
                        <h2 className="list-title glow-text">
                            {getTitleByType(type)}
                        </h2>
                    </div>
                    <div className="list-count">
                        Total: <strong>{items.length}</strong>
                    </div>
                </div>
            </div>

            <div className="table-container">
                <div className="table-wrapper">
                    <table className="data-table">
                        <thead>
                            <tr>
                                {renderTableHeaders()}
                            </tr>
                        </thead>
                        <tbody>
                            {items.map((item, index) => renderTableRow(item, index))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

export default ListView;