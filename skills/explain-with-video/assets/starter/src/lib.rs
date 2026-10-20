//! One continuous stage. The screen, the pointer, the lifted row and the
//! progress path are actors drawn by the video with global time. The two
//! scenes are chapters that only add their heading. Replace the actors and
//! chapters with the planned explanation; keep the structure.

use fframes::{AudioMap, Color, Duration, FFramesContext, Frame, Scene, Scenes, Svgr, Video};

const FONT: &str = "DM Sans";
const INK: &str = "#f2f6ff";
const MUTED: &str = "#b9c9de";
const BLUE: &str = "#8ab8fa";
const AMBER: &str = "#ffca63";
const GREEN: &str = "#70e0b3";
const TRACK: &str = "#243c59";

// timing helpers: every animation is a function of video seconds.

fn clamp01(x: f32) -> f32 {
    x.clamp(0.0, 1.0)
}

fn ease_out(p: f32) -> f32 {
    let q = 1.0 - clamp01(p);
    1.0 - q * q * q
}

fn ease_in_out(p: f32) -> f32 {
    let p = clamp01(p);
    if p < 0.5 {
        4.0 * p * p * p
    } else {
        1.0 - (-2.0 * p + 2.0).powi(3) / 2.0
    }
}

/// 0 before `start`, eased to 1 over `duration`.
fn rise(t: f32, start: f32, duration: f32) -> f32 {
    ease_out((t - start) / duration)
}

/// Like `rise`, with ease-in-out for things that travel.
fn glide(t: f32, start: f32, duration: f32) -> f32 {
    ease_in_out((t - start) / duration)
}

fn lerp(a: f32, b: f32, p: f32) -> f32 {
    a + (b - a) * p
}

/// Visible between `start` and `end`, with 0.4 s entrance and exit.
fn window(t: f32, start: f32, end: f32) -> f32 {
    rise(t, start, 0.4) * (1.0 - rise(t, end - 0.4, 0.4))
}

/// A short pulse: 0 outside [start, start + 0.35], peaking at 1 in the middle.
fn pulse(t: f32, start: f32) -> f32 {
    let q = (t - start) / 0.35;
    if (0.0..1.0).contains(&q) {
        (q * std::f32::consts::PI).sin()
    } else {
        0.0
    }
}

fn seconds(frame: &Frame) -> f32 {
    frame.global_index as f32 / ExplainerVideo::FPS as f32
}

// the screen actor: a list, then a confirmation, pushed in after a tap.

const SCREEN_X: f32 = 1256.0;
const SCREEN_Y: f32 = 136.0;
const ROW_X: f32 = 1280.0;
const ROW_W: f32 = 440.0;
const ROW_H: f32 = 72.0;
const ROW_Y: [f32; 4] = [240.0, 330.0, 420.0, 510.0];
const SUBJECT: usize = 2;
const TAP_ROW: f32 = 5.0;
const PUSH_AT: f32 = 5.2;
const TAP_CONFIRM: f32 = 6.2;

fn row<'a>(index: usize, dx: f32) -> Svgr<'a> {
    let names = ["steady-wren", "quiet-lynx", "calm-marmot", "gentle-heron"];
    let (status, color) = if index == SUBJECT {
        ("84% uptime this week", AMBER)
    } else {
        ("online", GREEN)
    };
    let x = ROW_X + dx;
    let y = ROW_Y[index];
    fframes::svgr!(<g>
        <rect x={x} y={y} width={ROW_W} height={ROW_H} rx="14" fill="#f4f7fb" />
        <circle cx={x + 28.0} cy={y + 36.0} r="7" fill={color} />
        <text x={x + 50.0} y={y + 32.0} font-size="24" fill="#111a26">{names[index]}</text>
        <text x={x + 50.0} y={y + 58.0} font-size="19" fill={if index == SUBJECT { "#8a5a00" } else { "#4f6579" }}>{status}</text>
    </g>)
}

fn screen_list<'a>(dx: f32) -> Svgr<'a> {
    let rows: Vec<_> = (0..4).map(|index| row(index, dx)).collect();
    let x = SCREEN_X + dx;
    fframes::svgr!(<g>
        <rect x={x} y={SCREEN_Y} width="488" height="808" fill="#ffffff" />
        <text x={x + 24.0} y="196" font-size="30" fill="#111a26">"Guardians"</text>
        {rows}
    </g>)
}

fn screen_confirm<'a>(dx: f32, t: f32) -> Svgr<'a> {
    let x = SCREEN_X + dx;
    let confirmed = rise(t, TAP_CONFIRM + 0.1, 0.5);
    let fill = if confirmed > 0.0 { GREEN } else { "#111a26" };
    let check_offset = 60.0 * (1.0 - confirmed);
    let press = 1.0 - 0.04 * pulse(t, TAP_CONFIRM);
    let (bx, by) = (x + 24.0, 700.0);
    let transform = format!(
        "translate({} {}) scale({})",
        (bx + 220.0) * (1.0 - press),
        (by + 36.0) * (1.0 - press),
        press
    );
    fframes::svgr!(<g>
        <rect x={x} y={SCREEN_Y} width="488" height="808" fill="#ffffff" />
        <text x={x + 24.0} y="196" font-size="30" fill="#111a26">"Replace calm-marmot"</text>
        <text x={x + 24.0} y="260" font-size="22" fill="#4f6579">"Seat price"</text>
        <text x={x + 24.0} y="306" font-size="38" fill="#111a26">"21,000 sats"</text>
        <g transform={transform}>
            <rect x={bx} y={by} width="440" height="72" rx="36" fill={fill} />
            <text x={bx + 220.0} y={by + 46.0} text-anchor="middle" font-size="26" fill={if confirmed > 0.0 { "#091320" } else { "#ffffff" }} opacity={1.0 - confirmed}>"Confirm"</text>
            <path d={format!("M{} {} L{} {} L{} {}", bx + 200.0, by + 36.0, bx + 214.0, by + 50.0, bx + 242.0, by + 22.0)} fill="none" stroke="#091320" stroke-width="6" stroke-linecap="round" stroke-dasharray="60" stroke-dashoffset={check_offset} opacity={confirmed} />
        </g>
    </g>)
}

fn screen<'a>(t: f32) -> Svgr<'a> {
    let p = glide(t, PUSH_AT, 0.4);
    let previous = if p < 1.0 {
        screen_list(-488.0 * p)
    } else {
        Svgr::empty()
    };
    let current = if p > 0.0 {
        screen_confirm(488.0 * (1.0 - p), t)
    } else {
        Svgr::empty()
    };
    fframes::svgr!(<g>
        <rect x="1240" y="120" width="520" height="840" rx="48" fill="#020911" stroke="#39516a" stroke-width="3" />
        <g clip-path="url(#screen)">{previous}{current}</g>
    </g>)
}

// the pointer: travels between waypoints, presses at taps.

const POINTER: [(f32, f32, f32); 6] = [
    (0.6, 1500.0, 880.0),
    (1.4, 1300.0, 456.0),
    (5.2, 1300.0, 456.0),
    (5.8, 1500.0, 736.0),
    (8.6, 1500.0, 736.0),
    (9.2, 1620.0, 880.0),
];
const TAPS: [(f32, f32, f32); 2] = [(TAP_ROW, 1300.0, 456.0), (TAP_CONFIRM, 1500.0, 736.0)];

fn pointer_position(t: f32) -> (f32, f32) {
    if t <= POINTER[0].0 {
        return (POINTER[0].1, POINTER[0].2);
    }
    for pair in POINTER.windows(2) {
        let (a, b) = (pair[0], pair[1]);
        if t >= a.0 && t < b.0 {
            let p = glide(t, a.0, b.0 - a.0);
            return (lerp(a.1, b.1, p), lerp(a.2, b.2, p));
        }
    }
    let last = POINTER[POINTER.len() - 1];
    (last.1, last.2)
}

fn pointer<'a>(t: f32) -> Svgr<'a> {
    let opacity = window(t, 0.6, 9.6);
    if opacity <= 0.0 {
        return Svgr::empty();
    }
    let (x, y) = pointer_position(t);
    let mut press = 1.0;
    let ripples: Vec<_> = TAPS
        .iter()
        .filter_map(|&(at, tx, ty)| {
            let q = (t - at) / 0.45;
            if (t - at).abs() < 0.12 {
                press = 0.78;
            }
            (0.0..1.0).contains(&q).then(|| {
                let r = 14.0 + 64.0 * q;
                let o = (1.0 - q) * 0.7;
                fframes::svgr!(<circle cx={tx} cy={ty} r={r} fill="none" stroke={BLUE} stroke-width="4" opacity={o} />)
            })
        })
        .collect();
    let r = 17.0 * press;
    fframes::svgr!(<g opacity={opacity}>
        {ripples}
        <circle cx={x} cy={y} r={r + 6.0} fill={BLUE} opacity="0.35" />
        <circle cx={x} cy={y} r={r} fill="#ffffff" stroke={BLUE} stroke-width="3" />
    </g>)
}

// the lifted row: the same row leaves the screen, grows, and returns.

const LIFT_START: f32 = 1.9;
const LIFT_END: f32 = 4.9;

fn lifted<'a>(t: f32) -> Svgr<'a> {
    let p = rise(t, LIFT_START, 0.8) * (1.0 - rise(t, LIFT_END - 0.5, 0.5));
    if p <= 0.0 {
        return Svgr::empty();
    }
    let (sx, sy) = (ROW_X, ROW_Y[SUBJECT]);
    let s = lerp(1.0, 2.0, p);
    let x = lerp(sx, 180.0, p);
    let y = lerp(sy, 440.0, p);
    let transform = format!("translate({} {}) scale({})", x - s * sx, y - s * sy, s);
    let right = x + ROW_W * s;
    let middle = y + ROW_H * s / 2.0;
    let connector = format!(
        "M{} {} H{} V{} H{}",
        right,
        middle,
        (right + sx) / 2.0,
        sy + ROW_H / 2.0,
        sx
    );
    fframes::svgr!(<g>
        <path d={connector} fill="none" stroke={BLUE} stroke-width="3" stroke-dasharray="8 10" opacity={p} />
        <rect x={sx - 4.0} y={sy - 4.0} width={ROW_W + 8.0} height={ROW_H + 8.0} rx="18" fill="none" stroke={BLUE} stroke-width="4" opacity={p} />
        <g transform={transform}>{row(SUBJECT, 0.0)}</g>
    </g>)
}

// the measure: a quantity grows against a fixed line while its number counts.

fn measure<'a>(t: f32) -> Svgr<'a> {
    let opacity = window(t, 2.8, 4.9);
    if opacity <= 0.0 {
        return Svgr::empty();
    }
    let p = rise(t, 2.9, 1.1);
    let width = (944.0 * 0.84 * p).max(0.5);
    let mark_x = 180.0 + 944.0 * 0.9;
    let text = format!("{:.0}% uptime this week", 84.0 * p);
    let tag = rise(t, 4.0, 0.4);
    let tag_y = lerp(690.0, 670.0, tag);
    fframes::svgr!(<g opacity={opacity}>
        <rect x="180" y="628" width="944" height="22" rx="6" fill={TRACK} />
        <rect x="180" y="628" width={width} height="22" rx="6" fill={AMBER} />
        <path d={format!("M{} 616 V662", mark_x)} stroke={INK} stroke-width="3" stroke-dasharray="6 6" />
        <text x={mark_x} y="698" text-anchor="middle" font-size="28" fill={INK}>"90%"</text>
        <text x="180" y="710" font-size="40" fill={AMBER}>{text}</text>
        <g opacity={tag}>
            <rect x="700" y={tag_y} width="260" height="56" rx="28" fill={AMBER} />
            <text x="830" y={tag_y + 38.0} text-anchor="middle" font-size="32" fill="#091320">"below the line"</text>
        </g>
    </g>)
}

// the path: a token travels through the stages as the viewer acts.

fn path<'a>(t: f32) -> Svgr<'a> {
    let opacity = window(t, TAP_ROW, 10.4);
    if opacity <= 0.0 {
        return Svgr::empty();
    }
    let y = 880.0;
    let xs = [260.0, 680.0, 1100.0];
    let labels = ["Row", "Confirm", "Done"];
    let position = glide(t, TAP_CONFIRM, 0.7) + glide(t, TAP_CONFIRM + 1.0, 0.8);
    let i = (position.floor() as usize).min(1);
    let token_x = lerp(xs[i], xs[i + 1], position - i as f32);
    let done = rise(t, TAP_CONFIRM + 1.8, 0.5);
    let stations: Vec<_> = xs
        .iter()
        .zip(labels)
        .enumerate()
        .map(|(index, (&x, label))| {
            let reached = position + 0.01 >= index as f32;
            let fill = if index == 2 && done > 0.0 { GREEN } else if reached { BLUE } else { TRACK };
            fframes::svgr!(<g>
                <circle cx={x} cy={y} r="24" fill={fill} stroke={if reached { fill } else { "#6b7b8e" }} stroke-width="2" />
                <text x={x} y={y + 64.0} text-anchor="middle" font-size="30" fill={if reached { INK } else { MUTED }}>{label}</text>
            </g>)
        })
        .collect();
    let replaced = rise(t, TAP_CONFIRM + 2.0, 0.5);
    fframes::svgr!(<g opacity={opacity}>
        <path d={format!("M{} {} H{}", xs[0], y, xs[2])} stroke="#3a506a" stroke-width="8" />
        <path d={format!("M{} {} H{}", xs[0], y, token_x)} stroke={BLUE} stroke-width="8" />
        {stations}
        <circle cx={token_x} cy={y} r="14" fill="#ffffff" stroke={BLUE} stroke-width="4" />
        <text x="680" y={y - 56.0} text-anchor="middle" font-size="34" fill={GREEN} opacity={replaced}>"calm-marmot replaced"</text>
    </g>)
}

// the video: stage underneath, chapters on top.

#[derive(Debug)]
pub struct ExplainerVideo {
    chapters: [Chapter; 2],
    captions: bool,
}

impl ExplainerVideo {
    pub fn new(captions: bool) -> Self {
        Self {
            captions,
            chapters: [
                Chapter {
                    name: "Condition",
                    frames: 150,
                    label: "ONE CONDITION",
                    title: "Is this row below the line?",
                },
                Chapter {
                    name: "Action",
                    frames: 150,
                    label: "ONE ACTION",
                    title: "Tap the row. Confirm.",
                },
            ],
        }
    }
}

impl Default for ExplainerVideo {
    fn default() -> Self {
        Self::new(false)
    }
}

impl Video for ExplainerVideo {
    const FPS: usize = 30;
    const WIDTH: usize = 1920;
    const HEIGHT: usize = 1080;
    const BACKGROUND_COLOR: Color = Color::BLACK;

    fn duration(&self) -> Duration<'_> {
        Duration::Auto
    }
    fn audio(&self) -> AudioMap<'_> {
        AudioMap::none()
    }
    fn define_scenes(&self) -> Scenes<'_> {
        Scenes::from(
            self.chapters
                .iter()
                .map(|chapter| chapter as &dyn Scene)
                .collect::<Vec<_>>(),
        )
    }

    fn render_frame<'a>(&'a self, frame: Frame, ctx: &FFramesContext<'a, '_>) -> Svgr<'a> {
        let t = seconds(&frame);
        let captions = if self.captions {
            caption_text(&frame, ctx)
        } else {
            Svgr::empty()
        };
        fframes::svgr!(<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080">
            <defs>
                <clipPath id="screen"><rect x={SCREEN_X} y={SCREEN_Y} width="488" height="808" rx="36" /></clipPath>
            </defs>
            <rect width="1920" height="1080" fill="#101c2b" />
            <g font-family={FONT} font-weight="500">
                {ctx.render_scenes(&frame)}
                {measure(t)}
                {path(t)}
                {screen(t)}
                {lifted(t)}
                {pointer(t)}
            </g>
            <rect y="978" width="1920" height="102" fill="#08111d" />
            {captions}
        </svg>)
    }
}

#[derive(Debug)]
struct Chapter {
    name: &'static str,
    frames: usize,
    label: &'static str,
    title: &'static str,
}

impl Scene for Chapter {
    fn name(&self) -> &'static str {
        self.name
    }
    fn duration(&self) -> Duration<'_> {
        Duration::Frames(self.frames)
    }
    fn audio(&self) -> AudioMap<'_> {
        AudioMap::none()
    }
    fn render_frame<'a>(&'a self, frame: Frame, _ctx: &FFramesContext<'a, '_>) -> Svgr<'a> {
        let local = frame.seconds();
        let length = self.frames as f32 / ExplainerVideo::FPS as f32;
        let enter = rise(local, 0.15, 0.5);
        let exit = rise(local, length - 0.45, 0.4);
        let opacity = enter * (1.0 - exit);
        let transform = format!("translate(0 {})", 24.0 * (1.0 - enter) - 24.0 * exit);
        fframes::svgr!(<g font-family={FONT} font-weight="500" opacity={opacity} transform={transform}>
            <text x="180" y="180" font-size="32" letter-spacing="3" fill={BLUE}>{self.label}</text>
            <text x="180" y="300" font-size="80" letter-spacing="-2" fill={INK}>{self.title}</text>
        </g>)
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
