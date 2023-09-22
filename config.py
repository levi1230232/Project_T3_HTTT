from sqlalchemy import create_engine

engine = create_engine(
    'sqlite:///Tinh_Hoc_Phi.db',
    connect_args={"timeout": 30},
)

