import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import PromptListPage from "./pages/PromptListPage.jsx";
import PromptCreatePage from "./pages/PromptCreatePage.jsx";
import PromptDetailPage from "./pages/PromptDetailPage.jsx";
import PromptEditPage from "./pages/PromptEditPage.jsx";
import CollectionListPage from "./pages/CollectionListPage.jsx";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/prompts" element={<PromptListPage />} />
        <Route path="/prompts/new" element={<PromptCreatePage />} />
        <Route path="/prompts/:id" element={<PromptDetailPage />} />
        <Route path="/prompts/:id/edit" element={<PromptEditPage />} />
        <Route path="/collections" element={<CollectionListPage />} />
        <Route path="/" element={<Navigate to="/prompts" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
