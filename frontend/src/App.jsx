import { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import SearchResults from './components/SearchResults';
import DetailModal from './components/DetailModal';
import ListView from './components/ListView';
import './App.css';

const API_BASE = 'http://127.0.0.1:8000';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [searchResults, setSearchResults] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null);
  const [listType, setListType] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  
  const [language, setLanguage] = useState('es');
  const [translations, setTranslations] = useState({});

  useEffect(() => {
    const loadTranslations = async () => {
      try {
        const response = await fetch(`${API_BASE}/config/idioma/${language}`);
        const data = await response.json();
        setTranslations(data);
        console.log('Traducciones cargadas:', data);
      } catch (error) {
        console.error('Error cargando traducciones:', error);
        setTranslations({});
      }
    };

    loadTranslations();
  }, [language]);

  const handleSearch = async (query, category, onlineMode) => {
    setIsSearching(true);
    try {
      const endpoint = onlineMode ? '/buscador/online' : '/buscador';
      const params = new URLSearchParams({ q: query });
      
      // Agregar parámetro de idioma
      params.append('lang', language);
      
      if (category && category !== 'Todo' && !onlineMode) {
        params.append('clase', category);
      }
      
      const response = await fetch(`${API_BASE}${endpoint}?${params}`);
      const data = await response.json();
      
      setSearchResults(data);
      setCurrentView('search');
    } catch (error) {
      console.error('Error en búsqueda:', error);
      setSearchResults({ cantidad: 0, resultados: [] });
    } finally {
      setIsSearching(false);
    }
  };

  const handleViewList = (type) => {
    setListType(type);
    setCurrentView('list');
  };

  const handleItemClick = async (itemId, itemData = null) => {
    if (itemData && itemData.origen === "DBpedia") {
      setSelectedItem(itemData);
      return;
    }

    if (typeof itemId === 'string' && itemId.startsWith('http://dbpedia.org')) {
      if (searchResults && searchResults.resultados) {
        const foundItem = searchResults.resultados.find(r => r.id === itemId);
        if (foundItem) {
          setSelectedItem(foundItem);
          return;
        }
      }
      setSelectedItem({
        id: itemId,
        nombre_mostrar: itemId.split('/').pop().replace(/_/g, ' '),
        tipo: 'DBpedia Resource',
        origen: 'DBpedia'
      });
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/individuos/${itemId}`);
      const data = await response.json();
      setSelectedItem(data);
    } catch (error) {
      console.error('Error cargando detalle:', error);
    }
  };

  const handleCloseModal = () => {
    setSelectedItem(null);
  };

  const handleNavigateToItem = async (itemId) => {
    handleCloseModal();
    setTimeout(() => handleItemClick(itemId), 100);
  };

  return (
    <div className="app">
      <Navbar 
        onSearch={handleSearch}
        onNavigate={(view) => {
          setCurrentView(view);
          setSearchResults(null);
        }}
        onViewList={handleViewList}
        language={language}
        setLanguage={setLanguage}
        translations={translations}
      />
      
      <main className="main-content">
        {currentView === 'dashboard' && (
          <Dashboard 
            onViewList={handleViewList}
            onItemClick={handleItemClick}
            translations={translations}
            language={language}
          />
        )}
        
        {currentView === 'search' && (
          <SearchResults 
            results={searchResults}
            onItemClick={handleItemClick}
            isSearching={isSearching}
            translations={translations}
            language={language}
          />
        )}
        
        {currentView === 'list' && listType && (
          <ListView 
            type={listType}
            onItemClick={handleItemClick}
            translations={translations}
            language={language}
          />
        )}
      </main>

      {selectedItem && (
        <DetailModal 
          item={selectedItem}
          onClose={handleCloseModal}
          onNavigate={handleNavigateToItem}
          translations={translations}
          language={language}
        />
      )}
    </div>
  );
}

export default App;