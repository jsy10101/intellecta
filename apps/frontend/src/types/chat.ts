export interface Room {
    id: number;
    name: string;
    type: "dm" | "group";
}

export interface Message {
    id: number;
    room: number;
    sender: number;
    body: string;
    created_at: string;
}
