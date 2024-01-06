from conans.test.utils.tools import GenConanfile, TestClient


def test_basic_parallel_download():
    client = TestClient(default_server_user=True)
    threads = 2
    counter = 4
    client.save({"global.conf": f"core.download:parallel={threads}"},
                path=client.cache.cache_folder)
    client.save({"conanfile.py": GenConanfile().with_option("myoption", '["ANY"]')})

    package_ids = []
    for i in range(counter):
        client.run(
            f"create . --name=pkg --version=0.1 --user=user --channel=testing -o pkg/*:myoption={i}"
        )
        package_id = client.created_package_id("pkg/0.1@user/testing")
        package_ids.append(package_id)
    client.run("upload * --confirm -r default")
    client.run("remove * -c")

    # Lets download the packages
    client.run("download pkg/0.1@user/testing#*:* -r default")
    assert f"Downloading recipes in {threads} parallel threads" in client.out
    assert (
        f"Downloading binary packages in {threads} parallel threads"
        in client.out
    )
    for package_id in package_ids:
        assert f"pkg/0.1@user/testing: Package installed {package_id}" in client.out
