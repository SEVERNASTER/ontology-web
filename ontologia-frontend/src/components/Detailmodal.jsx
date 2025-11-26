import './DetailModal.css';

function DetailModal({ item, onClose, onNavigate }) {
    if (!item) return null;

    // Detectar si es un resultado de DBpedia (online)
    const isOnlineResult = item.origen === "DBpedia (Online)" ||
        (typeof item.id === 'string' && item.id.startsWith('http://dbpedia.org'));

    const extractIdFromRelation = (relationText) => {
        const match = relationText.match(/\(ID:\s*([^)]+)\)/);
        return match ? match[1] : null;
    };

    const getBadgeClass = (clase) => {
        const claseLower = clase?.toLowerCase() || '';
        if (claseLower.includes('libro') || claseLower === 'book') return 'badge-libro';
        if (claseLower.includes('estudiante')) return 'badge-estudiante';
        if (claseLower.includes('docente')) return 'badge-docente';
        if (claseLower.includes('autor')) return 'badge-autor';
        if (claseLower.includes('editorial')) return 'badge-editorial';
        if (claseLower.includes('revista')) return 'badge-revista';
        if (claseLower.includes('bibliotecario')) return 'badge-bibliotecario';
        if (claseLower === 'person') return 'badge-autor';
        if (claseLower === 'place') return 'badge-editorial';
        if (claseLower === 'organisation' || claseLower === 'organization') return 'badge-editorial';
        return 'badge-libro';
    };

    const getIcon = (clase) => {
        const claseLower = clase?.toLowerCase() || '';
        if (claseLower.includes('libro') || claseLower === 'book') return '📖';
        if (claseLower.includes('estudiante')) return '🎓';
        if (claseLower.includes('docente')) return '👨‍🏫';
        if (claseLower.includes('autor')) return '✍️';
        if (claseLower.includes('editorial')) return '🏢';
        if (claseLower.includes('revista')) return '📰';
        if (claseLower.includes('bibliotecario')) return '👤';
        if (claseLower === 'person') return '👤';
        if (claseLower === 'place') return '📍';
        if (claseLower === 'organisation' || claseLower === 'organization') return '🏢';
        return '📄';
    };

    const formatKey = (key) => {
        return key
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    };

    // Función para preparar datos de DBpedia
    const prepareOnlineData = () => {
        const displayData = {};

        if (item.tipo) {
            displayData.tipo = [item.tipo];
        }

        if (item.descripcion && item.descripcion !== "Sin descripción") {
            displayData.descripcion = [item.descripcion];
        }

        if (item.origen) {
            displayData.origen = [item.origen];
        }

        // Si hay un campo 'url' o el id es una URL
        if (item.id && item.id.startsWith('http')) {
            displayData.url_dbpedia = [item.id];
        }

        return displayData;
    };

    // Determinar qué datos mostrar
    const displayName = item.nombre_mostrar || item.nombre || 'Sin nombre';
    const displayClass = item.clase || item.tipo || 'Desconocido';
    const displayData = isOnlineResult ? prepareOnlineData() : item.datos;
    const displayRelations = isOnlineResult ? {} : item.relaciones;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <button className="modal-close" onClick={onClose}>
                    ✕
                </button>

                <div className="modal-header">
                    <div className="modal-icon">{getIcon(displayClass)}</div>
                    <div className="modal-title-wrapper">
                        <h2 className="modal-title glow-text">{displayName}</h2>
                        <span className={`badge ${getBadgeClass(displayClass)}`}>
                            {displayClass}
                        </span>
                    </div>
                </div>

                <div className="modal-body">
                    {/* Imagen de DBpedia */}
                    {item.imagen && (
                        <div className="modal-image-section">
                            <img
                                src={item.imagen}
                                alt={displayName}
                                className="modal-image"
                                onError={(e) => {
                                    e.target.style.display = 'none';
                                    e.target.parentElement.style.display = 'none';
                                }}
                            />
                        </div>
                    )}

                    {/* Sección de Datos */}
                    {displayData && Object.keys(displayData).length > 0 && (
                        <div className="detail-section">
                            <h3 className="section-title">
                                <span className="section-icon">📋</span>
                                Información General
                            </h3>
                            <div className="detail-grid">
                                {Object.entries(displayData).map(([key, values]) => (
                                    <div key={key} className="detail-item fade-in">
                                        <div className="detail-label">{formatKey(key)}</div>
                                        <div className="detail-value">
                                            {Array.isArray(values)
                                                ? values.map((val, idx) => (
                                                    // Si es una URL, hacerla clickeable
                                                    key.toLowerCase().includes('url') || val.startsWith('http') ? (
                                                        <a
                                                            key={idx}
                                                            href={val}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="detail-value-link"
                                                        >
                                                            {val}
                                                        </a>
                                                    ) : (
                                                        <span key={idx} className="detail-value-chip">
                                                            {val}
                                                        </span>
                                                    )
                                                ))
                                                : (
                                                    key.toLowerCase().includes('url') || values.startsWith('http') ? (
                                                        <a
                                                            href={values}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="detail-value-link"
                                                        >
                                                            {values}
                                                        </a>
                                                    ) : values
                                                )
                                            }
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Sección de Relaciones (solo para búsqueda local) */}
                    {displayRelations && Object.keys(displayRelations).length > 0 && (
                        <div className="detail-section">
                            <h3 className="section-title">
                                <span className="section-icon">🔗</span>
                                Relaciones
                            </h3>
                            <div className="relations-grid">
                                {Object.entries(displayRelations).map(([key, values]) => (
                                    <div key={key} className="relation-group fade-in">
                                        <div className="relation-type">{formatKey(key)}</div>
                                        <div className="relation-items">
                                            {Array.isArray(values)
                                                ? values.map((val, idx) => {
                                                    const id = extractIdFromRelation(val);
                                                    const displayText = val.replace(/\s*\(ID:.*?\)/, '');

                                                    return (
                                                        <button
                                                            key={idx}
                                                            className="relation-chip"
                                                            onClick={() => id && onNavigate(id)}
                                                            disabled={!id}
                                                        >
                                                            <span className="relation-text">{displayText}</span>
                                                            {id && (
                                                                <span className="relation-arrow">→</span>
                                                            )}
                                                        </button>
                                                    );
                                                })
                                                : values
                                            }
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Si no hay datos ni relaciones */}
                    {(!displayData || Object.keys(displayData).length === 0) &&
                        (!displayRelations || Object.keys(displayRelations).length === 0) &&
                        !item.imagen && (
                            <div className="no-data">
                                <div className="no-data-icon">📭</div>
                                <p>No hay información adicional disponible para este elemento</p>
                            </div>
                        )}
                </div>

                <div className="modal-footer">
                    {isOnlineResult && item.id && item.id.startsWith('http') && (
                        <a
                            href={item.id}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn btn-primary"
                        >
                            Ver en DBpedia →
                        </a>
                    )}
                    <button className="btn btn-secondary" onClick={onClose}>
                        Cerrar
                    </button>
                </div>
            </div>
        </div>
    );
}

export default DetailModal;