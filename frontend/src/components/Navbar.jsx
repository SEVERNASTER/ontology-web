import { useState } from 'react';
import './Navbar.css';

function Navbar({ onSearch, onNavigate, onViewList, language, setLanguage, translations }) {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchCategory, setSearchCategory] = useState('Todo');
    const [menuOpen, setMenuOpen] = useState(false);
    const [onlineMode, setOnlineMode] = useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (searchQuery.trim()) {
            onSearch(searchQuery, searchCategory, onlineMode);
            setMenuOpen(false);
        }
    };

    // Función auxiliar para obtener traducción
    const t = (key) => translations[key] || key;

    return (
        <nav className="navbar">
            <div className="navbar-container">
                <div className="navbar-brand" onClick={() => onNavigate('dashboard')}>
                    <span className="brand-icon">📚</span>
                    <span className="brand-text glow-text">
                        {t('Biblioteca') || 'BiblioOntología'}
                    </span>
                </div>

                <form className="search-form" onSubmit={handleSubmit}>
                    <select
                        className="search-category"
                        value={searchCategory}
                        onChange={(e) => setSearchCategory(e.target.value)}
                    >
                        <option value="Todo">{t('Todo') || 'Todo'}</option>
                        <option value="Libro">{t('Libro') || 'Libros'}</option>
                        <option value="Estudiante">{t('Estudiante') || 'Estudiantes'}</option>
                        <option value="Docente">{t('Docente') || 'Docentes'}</option>
                        <option value="Autor">{t('Autor') || 'Autores'}</option>
                        <option value="Editorial">{t('Editorial') || 'Editoriales'}</option>
                    </select>

                    <input
                        type="text"
                        className="search-input"
                        placeholder={t('Buscar') || 'Buscar en la biblioteca...'}
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />

                    <button type="submit" className="search-button">
                        <span className="search-icon">🔍</span>
                    </button>

                    <div className="online-toggle">
                        <input
                            type="checkbox"
                            id="online-mode"
                            className="toggle-checkbox"
                            checked={onlineMode}
                            onChange={(e) => setOnlineMode(e.target.checked)}
                        />
                        <label htmlFor="online-mode" className="toggle-label">
                            <span className="toggle-inner"></span>
                            <span className="toggle-switch"></span>
                        </label>
                        <span className="toggle-text">
                            {onlineMode ? '🌐 DBpedia' : '💾 Local'}
                        </span>
                    </div>
                </form>

                {/* Selector de idioma */}
                <div className="language-selector">
                    <button
                        className={`lang-btn ${language === 'es' ? 'active' : ''}`}
                        onClick={() => setLanguage('es')}
                        title="Español"
                    >
                        🇪🇸 ES
                    </button>
                    <button
                        className={`lang-btn ${language === 'en' ? 'active' : ''}`}
                        onClick={() => setLanguage('en')}
                        title="English"
                    >
                        🇺🇸 EN
                    </button>
                </div>

                <button
                    className="menu-toggle"
                    onClick={() => setMenuOpen(!menuOpen)}
                >
                    ☰
                </button>

                <div className={`navbar-menu ${menuOpen ? 'active' : ''}`}>
                    <button
                        className="nav-link"
                        onClick={() => {
                            onNavigate('dashboard');
                            setMenuOpen(false);
                        }}
                    >
                        Dashboard
                    </button>
                    <button
                        className="nav-link"
                        onClick={() => {
                            onViewList('libros');
                            setMenuOpen(false);
                        }}
                    >
                        {t('Libro') || 'Libros'}
                    </button>
                    <button
                        className="nav-link"
                        onClick={() => {
                            onViewList('estudiantes');
                            setMenuOpen(false);
                        }}
                    >
                        {t('Estudiante') || 'Estudiantes'}
                    </button>
                    <button
                        className="nav-link"
                        onClick={() => {
                            onViewList('docentes');
                            setMenuOpen(false);
                        }}
                    >
                        {t('Docente') || 'Docentes'}
                    </button>
                    <button
                        className="nav-link"
                        onClick={() => {
                            onViewList('revistas');
                            setMenuOpen(false);
                        }}
                    >
                        {t('Revista') || 'Revistas'}
                    </button>
                    <button
                        className="nav-link"
                        onClick={() => {
                            onViewList('bibliotecarios');
                            setMenuOpen(false);
                        }}
                    >
                        {t('Bibliotecario') || 'Bibliotecarios'}
                    </button>
                </div>
            </div>
        </nav>
    );
}

export default Navbar;