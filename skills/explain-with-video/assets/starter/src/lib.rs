use fframes::{AudioMap, Color, Duration, FFramesContext, Frame, Svgr, Video, animation::Easing};

#[derive(Debug)]
pub struct ExplainerVideo {
    captions: bool,
}

impl ExplainerVideo {
    pub fn new(captions: bool) -> Self {
        Self { captions }
    }
}

impl Video for ExplainerVideo {
    const FPS: usize = 30;
    const WIDTH: usize = 1920;
    const HEIGHT: usize = 1080;
    const BACKGROUND_COLOR: Color = Color::BLACK;

    fn duration(&self) -> Duration<'_> {
        Duration::Seconds(8.0)
    }
    fn audio(&self) -> AudioMap<'_> {
        AudioMap::none()
    }

    fn render_frame<'a>(&'a self, frame: Frame, ctx: &FFramesContext<'a, '_>) -> Svgr<'a> {
        let captions = if self.captions {
            caption_text(&frame, ctx)
        } else {
            Svgr::empty()
        };
        fframes::svgr!(<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080">
            <rect width="1920" height="1080" fill="#101c2b" />
            <g font-family="DM Sans" font-weight="500">
                <text x="180" y="180" font-size="32" letter-spacing="3" fill="#8ab8fa">"ONE DECISION"</text>
                <text x="180" y="368" font-size="112" fill="#f2f6ff">"What should happen next?"</text>
                <g opacity={frame.animate(fframes::timeline!(at 0.4 => 1.0, animate 0.0 => 1.0, Easing::EaseOut,))}>
                    <rect x="180" y="490" width="740" height="270" rx="28" fill="#243c59" />
                    <text x="224" y="579" font-size="55" fill="#f2f6ff">"Show the condition"</text>
                    <text x="224" y="654" font-size="39" fill="#b9c9de">"Use one relevant fact."</text>
                </g>
                <g opacity={frame.animate(fframes::timeline!(at 1.1 => 1.7, animate 0.0 => 1.0, Easing::EaseOut,))}>
                    <rect x="1000" y="490" width="740" height="270" rx="28" fill="#213c37" />
                    <text x="1044" y="579" font-size="55" fill="#f2f6ff">"Show the action"</text>
                    <text x="1044" y="654" font-size="39" fill="#a7d8c8">"Make the result visible."</text>
                </g>
                <text x="180" y="891" font-size="38" fill="#b9c9de">"Condition and action stay visible together."</text>
            </g>
            <rect y="978" width="1920" height="102" fill="#08111d" />
            {captions}
        </svg>)
    }
}

fn caption_text<'a>(frame: &Frame, ctx: &FFramesContext<'a, '_>) -> Svgr<'a> {
    let phrase = ctx
        .get_subtitles("captions.vtt")
        .and_then(|subtitles| frame.get_subtitle_phrase(subtitles))
        .unwrap_or("");
    let line_count = phrase.split("<br>").count();
    let lines: Vec<_> = phrase.split("<br>").enumerate().map(|(index, line)| {
        let y = if line_count == 1 { 1040 } else { 1018 + index * 42 };
        fframes::svgr!(<text x="960" y={y} text-anchor="middle" font-family="DM Sans" font-weight="500" font-size="40" fill="#f2f6ff">{line}</text>)
    }).collect();
    fframes::svgr!(<g>{lines}</g>)
}
