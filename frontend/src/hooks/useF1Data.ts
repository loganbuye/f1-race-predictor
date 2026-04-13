import { useState, useEffect } from 'react';
import type { PredicitonResponse, DriverHistory } from '../types';

const API_BASE = "http://localhost:8000";

export function usePredictions(year: number) {
    const [data, setData] = useState<PredicitonResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        setLoading(true);
        setError(null);
        fetch(`${API_BASE}/predictions/${year}`)
            .then((res) => {
                if(!res.ok) throw new Error(`No upcoming race found for ${year}.`);
                return res.json();
            })
            .then(setData)
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false));
    }, [year]);
    return { data, loading, error };
}

export function useDriverHistory(driverNumber: number | null) {
    const [data, setData] = useState<DriverHistory | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if(driverNumber === null) return;
        setLoading(true);
        fetch(`${API_BASE}/driver_history/${driverNumber}`)
            .then((res) => res.json())
            .then(setData)
            .finally(() => setLoading(false));
    }, [driverNumber]);

    return { data, loading };
}