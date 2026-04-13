export interface Prediction {
    driver_name: string;
    team_name: string;
    grid_position: number;
    top10_probability: number;
}

export interface PredicitonResponse {
    year: number;
    predictions: Prediction[];
}

export interface DriverHistory {
    driver_number: number;
    finish_history: number[];
    avg_finish: number;
    races: number;
}