const API_BASE = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://localhost:8000/api"
    : "https://urban-data-explorer-api.onrender.com/api"; // L'utilisateur devra adapter l'URL finale

class UrbanAPI {
    static async getArrondissementsGeoJSON() {
        try {
            const res = await fetch(`${API_BASE}/arrondissements`);
            if (!res.ok) throw new Error("Erreur réseau");
            return await res.json();
        } catch (e) {
            console.error("API Error getArrondissements:", e);
            return null;
        }
    }

    static async getIndicators() {
        try {
            const res = await fetch(`${API_BASE}/indicateurs`);
            if (!res.ok) throw new Error("Erreur réseau");
            return await res.json();
        } catch (e) {
            console.error("API Error getIndicators:", e);
            return null;
        }
    }

    static async getDatasetGeoJSON(datasetName) {
        try {
            const res = await fetch(`${API_BASE}/dataset/${datasetName}?geojson=true`);
            if (!res.ok) throw new Error("Erreur réseau");
            return await res.json();
        } catch (e) {
            console.error(`API Error getDataset (${datasetName}):`, e);
            return null;
        }
    }

    static async getComparison(arr1, arr2) {
        try {
            const res = await fetch(`${API_BASE}/compare?a1=${arr1}&a2=${arr2}`);
            if (!res.ok) throw new Error("Erreur réseau");
            return await res.json();
        } catch (e) {
            console.error("API Error getComparison:", e);
            return null;
        }
    }
}
