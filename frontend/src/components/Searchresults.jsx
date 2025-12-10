import './SearchResults.css';

function SearchResults({ results, onItemClick, isSearching }) {
    if (isSearching) {
        return (
            <div className="search-results-loading">
                <div className="loading-spinner-large"></div>
                <h2 className="loading-title">Buscando en DBpedia...</h2>
                <p className="loading-message">
                    Esto puede tomar unos segundos mientras consultamos la base de datos externa
                </p>
            </div>
        );
    }

    if (!results || results.cantidad === 0) {
        return (
            <div className="search-results-empty">
                <div className="empty-icon">🔍</div>
                <h2 className="empty-title">No se encontraron resultados</h2>
                <p className="empty-message">
                    Intenta con otros términos de búsqueda o cambia el filtro de categoría
                </p>
            </div>
        );
    }

    const getBadgeClass = (tipo) => {
        const tipoLower = tipo.toLowerCase();
        if (tipoLower === 'libro') return 'badge-libro';
        if (tipoLower === 'estudiante') return 'badge-estudiante';
        if (tipoLower === 'docente') return 'badge-docente';
        if (tipoLower === 'autor') return 'badge-autor';
        if (tipoLower === 'editorial') return 'badge-editorial';
        if (tipoLower === 'revista') return 'badge-revista';
        if (tipoLower === 'bibliotecario') return 'badge-bibliotecario';
        return 'badge-libro';
    };

    const getIcon = (tipo) => {
        const tipoLower = tipo.toLowerCase();
        if (tipoLower === 'libro') return '📖';
        if (tipoLower === 'estudiante') return '🎓';
        if (tipoLower === 'docente') return '👨‍🏫';
        if (tipoLower === 'autor') return '✍️';
        if (tipoLower === 'editorial') return '🏢';
        if (tipoLower === 'revista') return '📰';
        if (tipoLower === 'bibliotecario') return '👤';
        return '📄';
    };

    return (
        <div className="search-results">
            <div className="search-results-header">
                <h2 className="results-title glow-text">
                    Resultados de Búsqueda
                </h2>
                <div className="results-count">
                    {results.cantidad} {results.cantidad === 1 ? 'resultado' : 'resultados'} encontrado{results.cantidad === 1 ? '' : 's'}
                </div>
            </div>

            <div className="results-grid">
                {results.resultados.map((item, index) => (
                    <div
                        key={`${item.id}-${index}`}
                        className="result-card fade-in"
                        style={{ animationDelay: `${index * 0.1}s` }}
                        onClick={() => {
                            if (item.origen === "DBpedia") {
                                onItemClick(item.id, item);
                            } else {
                                onItemClick(item.id);
                            }
                        }}
                    >
                        {item.imagen && (
                            <div className="result-image-container">
                                <img
                                    src={item.imagen}
                                    alt={item.nombre_mostrar}
                                    className="result-image"
                                    onError={(e) => e.target.style.display = 'none'}
                                />
                            </div>
                        )}

                        <div className="result-card-header">
                            <span className="result-icon">{getIcon(item.tipo)}</span>
                            <div className="result-badges">
                                <span className={`badge ${getBadgeClass(item.tipo)}`}>
                                    {item.tipo}
                                </span>
                                {item.origen && (
                                    <span className={`badge-origin ${item.origen === 'Local' ? 'badge-origin-local' : 'badge-origin-dbpedia'}`}>
                                        {item.origen === 'Local' ? (
                                            <>💾 Local</>
                                        ) : (
                                            <>🌐 DBpedia</>
                                        )}
                                    </span>
                                )}
                            </div>
                        </div>

                        <h3 className="result-name">{item.nombre_mostrar}</h3>

                        {item.descripcion && item.descripcion !== "Sin descripción" && (
                            <p className="result-description">{item.descripcion}</p>
                        )}

                        <div className="result-footer">
                            <span className="result-id" title={item.id}>
                                {item.id.length > 30 ? `${item.id.substring(0, 30)}...` : item.id}
                            </span>
                            <span className="result-action">Ver detalles →</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default SearchResults;