use fframes::cli::clap;
use fframes::{EncoderOptions, MediaDirectory, MediaProvider, RenderOptions, cli};
use fframes_skia_renderer::{SkiaPipelineConfig, cli::SkiaRenderers};
use std::{error::Error, path::Path, process::ExitCode};
use video_explainer::ExplainerVideo;

#[derive(Debug, clap::Args)]
struct VideoArgs {
    #[arg(long, global = true)]
    captions: bool,
}

fn run() -> Result<ExitCode, Box<dyn Error>> {
    let args = cli::parse::<VideoArgs>();
    let folder = MediaDirectory::read_folder(Path::new(env!("CARGO_MANIFEST_DIR")).join("media"))?;
    let media = folder.process_media_source()?;
    if args.app.captions && media.resolve_subtitles("captions.vtt").is_none() {
        return Err("--captions requires media/captions.vtt".into());
    }
    let video = ExplainerVideo::new(args.app.captions);
    Ok(cli::new(
        &video,
        RenderOptions {
            media: Some(&media),
            load_system_fonts: false,
            video_encoder_options: EncoderOptions {
                preferred_encoder: Some("libx264"),
                codec_params: Some(&[("crf", "18"), ("preset", "medium"), ("tune", "animation")]),
                ..Default::default()
            },
            ..Default::default()
        },
    )
    .args(args)
    .renderers(SkiaRenderers::gpu(SkiaPipelineConfig::default()))
    .preview(fframes_native_player::cli_preview)
    .default_output("explainer.mp4")
    .run())
}

fn main() -> ExitCode {
    match run() {
        Ok(code) => code,
        Err(error) => {
            eprintln!("video: {error}");
            ExitCode::FAILURE
        }
    }
}
