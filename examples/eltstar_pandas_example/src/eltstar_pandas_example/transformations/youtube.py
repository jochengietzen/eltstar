import pandas as pd
from eltstar_engine_pandas.functions.join import PandasJoinArgSpec

from eltstar.models.data_frame_wrapper.preloaded_wrapper import DataFrameWrapper, TypedDataFrameWrapper
from eltstar.transformation import manager
from eltstar_pandas_example.models.youtube import (
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
def youtube_channel_overview(
    tech_videos: TypedDataFrameWrapper[pd.DataFrame], tech_channels: TypedDataFrameWrapper[pd.DataFrame]
):
    tech_channel_overview = tech_channels.join(
        function_spec=PandasJoinArgSpec(other=tech_videos, left_on=["channel_id"], right_on=["channel_id"], how="left")
    )
    tech_channel_overview = tech_channel_overview.create_with_new_data(
        data_frame=tech_channel_overview.data_frame.groupby("channel_id")
        .agg(
            channel_views=("views", "sum"),
            channel_likes=("likes", "sum"),
        )
        .reset_index()
    )
    tech_channel_overview = tech_channel_overview.join(
        PandasJoinArgSpec(
            other=DataFrameWrapper(data_frame=tech_channels.data_frame[["channel_id", "channel_name"]]),
            left_on=["channel_id"],
            right_on=["channel_id"],
            how="inner",
        )
    )
    tech_channel_overview.data_frame.sort_values("channel_id", inplace=True)
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
