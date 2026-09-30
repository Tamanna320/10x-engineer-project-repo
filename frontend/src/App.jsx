import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import PromptListPage from "./pages/PromptListPage.jsx";
import PromptCreatePage from "./pages/PromptCreatePage.jsx";
import PromptDetailPage from "./pages/PromptDetailPage.jsx";
import PromptEditPage from "./pages/PromptEditPage.jsx";
import CollectionListPage from "./pages/CollectionListPage.jsx";
import Layout from "./components/Layout.jsx";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/prompts"
          element={
            <Layout>
              <PromptListPage />
            </Layout>
          }
        />
        <Route
          path="/prompts/new"
          element={
            <Layout>
              <PromptCreatePage />
            </Layout>
          }
        />
        <Route
          path="/prompts/:id"
          element={
            <Layout>
              <PromptDetailPage />
            </Layout>
          }
        />
        <Route
          path="/prompts/:id/edit"
          element={
            <Layout>
              <PromptEditPage />
            </Layout>
          }
        />
        <Route
          path="/collections"
          element={
            <Layout>
              <CollectionListPage />
            </Layout>
          }
        />
        <Route path="/" element={<Navigate to="/prompts" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
