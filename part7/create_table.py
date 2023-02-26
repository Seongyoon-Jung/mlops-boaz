# create_table.py
import psycopg2

def create_table(db_connect):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS breast_cancer (
        id SERIAL PRIMARY KEY,
        timestamp timestamp,
        mean_radius float8,
        mean_texture float8,
        mean_perimeter float8,
        mean_area float8,
        mean_smoothness float8,
        mean_compactness float8,
        mean_concavity float8,
        mean_concave_points float8,
        mean_symmetry float8,
        mean_fractal_dimension float8,
        radius_error float8,
        texture_error float8,
        perimeter_error float8,
        area_error float8,
        smoothness_error float8,
        compactness_error float8,
        concavity_error float8,
        concave_points_error float8,
        symmetry_error float8,
        fractal_dimension_error float8,
        worst_radius float8,
        worst_texture float8,
        worst_perimeter float8,
        worst_area float8,
        worst_smoothness float8,
        worst_compactness float8,
        worst_concavity float8,
        worst_concave_points float8,
        worst_symmetry float8,
        worst_fractal_dimension float8,
        target int
    );"""
    print(create_table_query)
    with db_connect.cursor() as cur:
        cur.execute(create_table_query)
        db_connect.commit()



if __name__ == "__main__":
    db_connect = psycopg2.connect(
        user="targetuser",
        password="targetpassword",
        host="target-postgres-server",
        port=5432,
        database="targetdatabase",
    )
    create_table(db_connect)
