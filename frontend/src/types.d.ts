export { }

declare global {
    interface Window {
        SpeechRecognition: any;
        webkitSpeechRecognition: any;
        electron?: {
            minimize: () => void;
            maximize: () => void;
            close: () => void;
        };
    }
}
