import polars as pl

from eltstar.models.data_frame_wrapper import DataFrameWrapper
from eltstar.transformation import manager
from eltstar_polars_example.models.youtube import (
    tech_channel_overview,
    tech_channel_overview_2,
    tech_channel_overview_3,
    tech_channels,
    tech_videos,
)


@manager.register_transformation(
    output_table_model=tech_channel_overview,
    tech_videos=tech_videos,
    tech_channels=tech_channels,
)
def youtube_channel_overview(tech_videos: DataFrameWrapper, tech_channels: DataFrameWrapper):
    tech_channel_overview = tech_channels.data_frame.join(tech_videos.data_frame, on="channel_id", how="left")
    tech_channel_overview = (
        tech_channel_overview.group_by("channel_id")
        .agg(
            pl.sum("views").alias("channel_views"),
            pl.sum("likes").alias("channel_likes"),
        )
        .join(
            tech_channels.data_frame.select(["channel_id", "channel_name"]),
            on="channel_id",
            how="inner",
        )
    )
    return tech_channel_overview


# @manager.register_transformation(
#     output_table_model=tech_channel_overview,
#     tech_videos=tech_videos,
#     tech_channels=tech_channels,
# )
# def youtube_channel_overview_failing(tech_videos: DataFrameWrapper, tech_channels: DataFrameWrapper):
#     tech_channel_overview = tech_channels.data_frame.join(tech_videos.data_frame, on="channel_id", how="left")
#     tech_channel_overview = (
#         tech_channel_overview.group_by("channel_id")
#         .agg(
#             pl.sum("views").alias("channel_views"),
#             pl.sum("likes").alias("channel_likes"),
#         )
#         .join(
#             tech_channels.data_frame.select(["channel_id", "channel_name"]),
#             on="channel_id",
#             how="inner",
#         )
#         .select("channel_views", "foo")
#     )
#     return tech_channel_overview


@manager.register_transformation(
    output_table_model=tech_channel_overview_2,
    tech_videos=tech_videos,
    tech_channel_overview=tech_channel_overview,
)
def youtube_channel_overview_2(tech_videos: DataFrameWrapper, tech_channel_overview: DataFrameWrapper):
    return tech_channel_overview


@manager.register_transformation(
    output_table_model=tech_channel_overview_3,
    tech_videos=tech_videos,
)
def youtube_channel_overview_3(tech_videos: DataFrameWrapper):
    return tech_videos
